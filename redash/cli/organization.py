from click import argument
from flask.cli import AppGroup

from redash import models

manager = AppGroup(help="Organization management commands.")


@manager.command()
@argument("domains")
def set_google_apps_domains(domains):
    """
    Sets the allowable domains to the comma separated list DOMAINS.
    """
    organization = models.Organization.query.first()
    k = models.Organization.SETTING_GOOGLE_APPS_DOMAINS
    organization.settings[k] = domains.split(",")
    models.db.session.add(organization)
    models.db.session.commit()
    print(
        "Updated list of allowed domains to: {}".format(
            organization.google_apps_domains
        )
    )


@manager.command()
def show_google_apps_domains():
    organization = models.Organization.query.first()
    print(
        "Current list of Google Apps domains: {}".format(
            ", ".join(organization.google_apps_domains)
        )
    )

@manager.command()
@argument("domains")
def set_azure_apps_domains(domains):
    """
    Sets the allowable domains to the comma separated list DOMAINS.
    """
    organization = models.Organization.query.first()
    k = models.Organization.SETTING_AZURE_APPS_DOMAINS
    organization.settings[k] = domains.split(",")
    models.db.session.add(organization)
    models.db.session.commit()
    print(
        "Updated list of allowed domains to: {}".format(
            organization.azure_apps_domains
        )
    )

@manager.command()
def show_azure_apps_domains():
    organization = models.Organization.query.first()
    print(
        "Current list of Azure Apps domains: {}".format(
            ", ".join(organization.azure_apps_domains)
        )
    )


@manager.command()
@argument("roles")
def set_azure_roles(roles):
    """
    Sets the allowable roles to the comma separated list ROLES.
    """
    organization = models.Organization.query.first()
    k = models.Organization.SETTING_AZURE_ROLES
    organization.settings[k] = roles.split(",")
    models.db.session.add(organization)
    models.db.session.commit()
    print(
        "Updated list of allowed roles to: {}".format(
            organization.azure_roles
        )
    )

@manager.command()
def show_azure_roles():
    organization = models.Organization.query.first()
    print(
        "Current list of Azure roles: {}".format(
            ", ".join(organization.azure_roles)
        )
    )

@manager.command(name="list")
def list_command():
    """List all organizations"""
    orgs = models.Organization.query
    for i, org in enumerate(orgs.order_by(models.Organization.name)):
        if i > 0:
            print("-" * 20)

        print("Id: {}\nName: {}\nSlug: {}".format(org.id, org.name, org.slug))
