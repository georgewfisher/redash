import logging

from redash.query_runner import *
from redash.utils import json_dumps, json_loads
from trino.auth import JWTAuthentication
from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

try:
    import trino
    from trino.exceptions import DatabaseError

    enabled = True
except ImportError:
    enabled = False

TRINO_TYPES_MAPPING = {
    "boolean": TYPE_BOOLEAN,

    "tinyint": TYPE_INTEGER,
    "smallint": TYPE_INTEGER,
    "integer": TYPE_INTEGER,
    "long": TYPE_INTEGER,
    "bigint": TYPE_INTEGER,

    "float": TYPE_FLOAT,
    "real": TYPE_FLOAT,
    "double": TYPE_FLOAT,

    "decimal": TYPE_INTEGER,

    "varchar": TYPE_STRING,
    "char": TYPE_STRING,
    "string": TYPE_STRING,
    "json": TYPE_STRING,

    "varbinary": TYPE_STRING,
    
    "date": TYPE_DATE,
    "timestamp": TYPE_DATETIME,
}


class AzureTrino(BaseQueryRunner):
    noop_query = "SELECT 1"
    should_annotate_query = False

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "title": "Trino Cluster Hostname"
                },
                "catalog": {
                    "type": "string",
                    "default": "system",
                    "title": "Default Catalog"
                },
                "schema": {
                    "type": "string",
                    "title": "Default Schema"
                },
                "use_msi": {
                    "type": "boolean",
                    "default": True,
                    "title": "Use Managed Service Identity (MSI)"
                },
                "azure_ad_client_id": {
                    "type": "string",
                    "title": "Azure AD Client ID (required for application auth, optional for MSI)"
                },
                "azure_ad_client_secret": {
                    "type": "string",
                    "title": "Azure AD Client Secret (required if not using MSI)",
                },
                "azure_ad_tenant_id": {
                    "type": "string",
                    "title": "Azure AD Tenant Id (required if not using MSI)"
                },
            },
            "order": [
                "host",
                "catalog",
                "schema",
                "use_msi",
                "azure_ad_client_id",
                "azure_ad_client_secret",
                "azure_ad_tenant_id",
            ],
            "required": [
                "host"
            ],
            "secret": [
                "azure_ad_client_secret"
            ]
        }

    @classmethod
    def enabled(cls):
        return enabled

    @classmethod
    def type(cls):
        return "azure_trino"

    @classmethod
    def name(cls):
        return "Azure Trino"

    def get_schema(self, get_stats=False):
        query = """
            SELECT table_schema, table_name, column_name
            FROM information_schema.columns
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """
        results, error = self.run_query(query, None)

        if error is not None:
            raise Exception("Failed getting schema.")

        results = json_loads(results)
        schema = {}
        for row in results["rows"]:
            table_name = f'{row["table_schema"]}.{row["table_name"]}'

            if table_name not in schema:
                schema[table_name] = {"name": table_name, "columns": []}

            schema[table_name]["columns"].append(row["column_name"])

        return list(schema.values())

    def run_query(self, query, user):

        azure_trino_scope = 'https://hilo.azurehdinsight.net/.default'

        if self.configuration.get("use_msi") == True:
            if not self.configuration.get("azure_ad_client_id"):
                credential = DefaultAzureCredential()
            else:
                credential = DefaultAzureCredential(managed_identity_client_id=self.configuration.get("azure_ad_client_id"))
        else:
            credential = ClientSecretCredential(self.configuration.get("azure_ad_tenant_id"), self.configuration.get("azure_ad_client_id"), self.configuration.get("azure_ad_client_secret"))
        
        if (user and user.name and user.email):
            queryWithUser = "/* {{\"name\":\"{name}\",\"email\":\"{email}\"}} */\n{querytext}".format(name = user.name, email = user.email, querytext = query)
            user_email = user.email
        else:
            queryWithUser = query
            user_email = "no_user"

        token = credential.get_token(azure_trino_scope)
        auth = JWTAuthentication(token.token)
        connection = trino.dbapi.connect(
            host=self.configuration.get("host", ""),
            catalog=self.configuration.get("catalog", ""),
            schema=self.configuration.get("schema", ""),
            auth=auth,
            http_scheme="https",
            port=443,
            user=user_email
        )
        cursor = connection.cursor()
        try:
            cursor.execute(queryWithUser)
            results = cursor.fetchall()
            description = cursor.description
            columns = self.fetch_columns([
                (c[0], TRINO_TYPES_MAPPING.get(c[1], None)) for c in description
            ])
            rows = [
                dict(zip([c["name"] for c in columns], r))
                for r in results
            ]
            data = {
                "columns": columns,
                "rows": rows
            }
            json_data = json_dumps(data)
            error = None
        except DatabaseError as db:
            json_data = None
            default_message = "Unspecified DatabaseError: {0}".format(str(db))
            if isinstance(db.args[0], dict):
                message = db.args[0].get("failureInfo", {"message", None}).get("message")
            else:
                message = None
            error = default_message if message is None else message
        except (KeyboardInterrupt, InterruptException, JobTimeoutException):
            cursor.cancel()
            raise

        return json_data, error


register(AzureTrino)