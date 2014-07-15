from django.contrib import admin
from oauth.models import Consumer, RequestToken, AccessToken, Nonce


class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('user', 'consumer_key', 'consumer_secret')


class RequestTokenAdmin(admin.ModelAdmin):
    list_display = ('request_token', 'request_token_secret', 'verifier')


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'access_token_secret', 'modified_at')
    list_filter = ['modified_at']
    search_fields = ['user__email']

class NonceAdmin(admin.ModelAdmin):
    list_display = ('consumer_key','nonce', 'timestamp')
    list_filter = ['timestamp']

admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(RequestToken, RequestTokenAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(Nonce, NonceAdmin)
