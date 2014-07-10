from django.contrib import admin
from users.models import StacksyncUser, StacksyncWorkspace, StacksyncMembership

class StacksyncMembershipInline(admin.StackedInline):
    model = StacksyncMembership
    fields = ['name']
    extra = 1


class StacksyncWorkspaceAdmin(admin.ModelAdmin):
    inlines = [StacksyncMembershipInline]


class StacksyncUserAdmin(admin.ModelAdmin):
    #inlines = [StacksyncMembershipInline]
    fields = ['name', 'email']
    list_display = ('name', 'email', 'swift_user', 'swift_account')
    actions = ['custom_delete']

    def get_actions(self, request):
        actions = super(StacksyncUserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def custom_delete(self, request, queryset):
            for user in queryset:
                user.delete()
    custom_delete.short_description = "Delete selected stacksync users"

admin.site.register(StacksyncUser, StacksyncUserAdmin)
admin.site.register(StacksyncWorkspace, StacksyncWorkspaceAdmin)
