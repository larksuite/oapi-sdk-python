from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.collaboration_tenant: CollaborationTenant = CollaborationTenant(config)
        self.collaboration_tenant_collaboration_department: CollaborationTenantCollaborationDepartment = CollaborationTenantCollaborationDepartment(
            config)
        self.collaboration_tenant_collaboration_user: CollaborationTenantCollaborationUser = CollaborationTenantCollaborationUser(
            config)
