from django.contrib import admin
from workspace.models import Workspace, WorkspaceConfig, EnvironmentVariable, KubernetesTemplate

admin.site.register(Workspace)
admin.site.register(WorkspaceConfig)
admin.site.register(EnvironmentVariable)
admin.site.register(KubernetesTemplate)
