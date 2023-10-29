# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def open_action(self):
        # Extends 'account_accountant'
        self.ensure_one()
        if not self._context.get('action_name') and self.type == 'bank' and self.bank_statements_source == 'online_sync':
            return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
                default_context={'search_default_journal_id': self.id},
            )
        return super().open_action()

    def __get_bank_statements_available_sources(self):
        rslt = super(AccountJournal, self).__get_bank_statements_available_sources()
        rslt.append(("online_sync", _("Automated Bank Synchronization")))
        return rslt

    next_link_synchronization = fields.Datetime("Online Link Next synchronization", related='account_online_link_id.next_refresh')
    expiring_synchronization_date = fields.Date(related='account_online_link_id.expiring_synchronization_date')
    expiring_synchronization_due_day = fields.Integer(compute='_compute_expiring_synchronization_due_day')
    account_online_account_id = fields.Many2one('account.online.account', copy=False, ondelete='set null')
    account_online_link_id = fields.Many2one('account.online.link', related='account_online_account_id.account_online_link_id', readonly=True, store=True)
    account_online_link_state = fields.Selection(related="account_online_link_id.state", readonly=True)
    renewal_contact_email = fields.Char(
        string='Connection Requests',
        help='Comma separated list of email addresses to send consent renewal notifications 15, 3 and 1 days before expiry',
        default=lambda self: self.env.user.email,
    )

    def write(self, vals):
        # When changing the bank_statement_source, unlink the connection if there is any
        if 'bank_statements_source' in vals and vals.get('bank_statements_source') != 'online_sync':
            for journal in self:
                if journal.bank_statements_source == 'online_sync':
                    # unlink current connection
                    vals['account_online_account_id'] = False
                    journal.account_online_link_id.has_unlinked_accounts = True
        return super().write(vals)

    @api.depends('expiring_synchronization_date')
    def _compute_expiring_synchronization_due_day(self):
        for record in self:
            if record.expiring_synchronization_date:
                due_day_delta = record.expiring_synchronization_date - fields.Date.context_today(record)
                record.expiring_synchronization_due_day = due_day_delta.days
            else:
                record.expiring_synchronization_due_day = 0

    @api.constrains('account_online_account_id')
    def _check_account_online_account_id(self):
        if len(self.account_online_account_id.journal_ids) > 1:
            raise ValidationError(_('You cannot have two journals associated with the same Online Account.'))

    @api.model
    def _cron_fetch_online_transactions(self):
        for journal in self.search([('account_online_account_id', '!=', False)]):
            if journal.account_online_link_id.auto_sync:
                try:
                    journal.with_context(cron=True).manual_sync()
                    # for cron jobs it is usually recommended committing after each iteration,
                    # so that a later error or job timeout doesn't discard previous work
                    self.env.cr.commit()
                except (UserError, RedirectWarning):
                    # We need to rollback here otherwise the next iteration will still have the error when trying to commit
                    self.env.cr.rollback()
                    pass

    @api.model
    def _cron_send_reminder_email(self):
        for journal in self.search([('account_online_account_id', '!=', False)]):
            if journal.expiring_synchronization_due_day in {1, 3, 15}:
                journal.action_send_reminder()

    def manual_sync(self):
        self.ensure_one()
        if self.account_online_link_id:
            account = self.account_online_account_id
            return self.account_online_link_id.with_context(dont_show_transactions=True)._fetch_transactions(accounts=account)

    def unlink(self):
        """
        Override of the unlink method.
        That's useful to unlink account.online.account too.
        """
        if self.account_online_account_id:
            self.account_online_account_id.unlink()
        return super(AccountJournal, self).unlink()

    def action_configure_bank_journal(self):
        """
        Override the "action_configure_bank_journal" and change the flow for the
        "Configure" button in dashboard.
        """
        self.ensure_one()
        return self.env['account.online.link'].action_new_synchronization()

    def action_open_account_online_link(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.account_online_link_id.name,
            'res_model': 'account.online.link',
            'target': 'main',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'res_id': self.account_online_link_id.id,
        }

    def action_extend_consent(self):
        """
        Extend the consent of the user by redirecting him to update his credentials
        """
        self.ensure_one()
        return self.account_online_link_id.action_update_credentials()

    def action_reconnect_online_account(self):
        self.ensure_one()
        return self.account_online_link_id.action_reconnect_account()

    def action_send_reminder(self):
        self.ensure_one()
        self._portal_ensure_token()
        template = self.env.ref('account_online_synchronization.email_template_sync_reminder')
        subtype = self.env.ref('account_online_synchronization.bank_sync_consent_renewal')
        self.message_post_with_source(source_ref=template, subtype_id=subtype.id)

    def action_open_missing_transaction_wizard(self):
        """ This method allows to open the wizard to fetch the missing
            transactions and the pending ones.
            Depending on where the function is called, we'll receive
            one journal or none of them.
            If we receive more or less than one journal, we do not set
            it on the wizard, the user should select it by himself.

            :return: An action opening the wizard.
        """
        journal_id = None
        if len(self) == 1:
            if not self.account_online_account_id or self.account_online_link_state != 'connected':
                raise UserError(_("You can't find missing transactions for a journal that isn't connected."))

            journal_id = self.id

        wizard = self.env['account.missing.transaction.wizard'].create({'journal_id': journal_id})
        return {
            'name': _("Find Missing Transactions"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.missing.transaction.wizard',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
