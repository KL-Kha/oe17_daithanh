/** @odoo-module */

import { CharField, charField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { renderToElement } from "@web/core/utils/render";
import { useEffect, useRef } from "@odoo/owl";

export class TwitterUsersAutocompleteField extends CharField {
    setup() {
        super.setup();

        this.orm = useService("orm");
        this.input = useRef('input');

        useEffect(() => {
            $(this.input.el).autocomplete({
                classes: {'ui-autocomplete': 'o_social_twitter_users_autocomplete'},
                source: async (request, response) => {
                    const accountId = this.props.record.data.account_id[0];

                    const userInfo = await this.orm.call(
                        'social.account',
                        'twitter_get_user_by_username',
                        [[accountId], request.term]
                    );
                    response(userInfo ? [userInfo] : []);
                },
                select: (ev, ui) => {
                    $(this.input.el).val(ui.item.name);
                    this.selectTwitterUser(ui.item);
                    ev.preventDefault();
                },
                html: true,
                minLength: 2,
                delay: 500,
            }).data('ui-autocomplete')._renderItem = function (ul, item){
                return $(renderToElement('social_twitter.users_autocomplete_element', {
                    suggestion: item
                })).appendTo(ul);
            };
        });
    }

    async selectTwitterUser(twitterUser) {
        const twitterAccountId = await this.orm.call(
            'social.twitter.account',
            'create',
            [{
                name: twitterUser.name,
                twitter_id: twitterUser.id
            }]
        );

        await this.props.record.update({
            twitter_followed_account_id: [twitterAccountId, twitterUser.name]
        });
    }
}

export const twitterUsersAutocompleteField = {
    ...charField,
    component: TwitterUsersAutocompleteField,
};

registry.category("fields").add("twitter_users_autocomplete", twitterUsersAutocompleteField);
