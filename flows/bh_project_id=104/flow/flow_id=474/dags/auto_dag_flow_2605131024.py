
from airflow import DAG
from datetime import datetime, timedelta
from airflow_plugins.dag_task_definitions.common_task import CommonTask
from airflow_plugins.dag_task_definitions.lineage_task import LineageTask

common_task = CommonTask(dag_id='auto_dag_flow_2605131024', dag_params={})
lineage_task = LineageTask(dag_id='auto_dag_flow_2605131024', dag_params={})

default_args = {
    'owner': 'bh',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 0
}

with DAG(
    dag_id='auto_dag_flow_2605131024',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=[]
) as dag:


    from airflow.operators.python import PythonOperator
    start_flow_task = PythonOperator(
        task_id='start_flow_task',
        python_callable=common_task.start_dag_task,
        on_success_callback=common_task.success_callback,
        on_failure_callback=common_task.failure_callback,
        params = {
            'flow_id': 474,
            'flow_name': 'auto-dag-flow-2605131024',
            'flow_key': 'auto_dag_flow_2605131024',
            'bh_project_id': 104,
            'project_name': 'bighammer',
            'flow_tags': [],
            'flow_type': 'INGESTION',
            'tenant_id': 113,
            'flow_status': 'In Progress',
        }
    )

    from airflow.operators.python import PythonOperator
    from airflow.providers.databricks.hooks.databricks import DatabricksHook

    def create_databricks_cluster_create_compute_d2b5c2a85(**context):
        from airflow_plugins.cloud_factory import CloudFactory
        hook = DatabricksHook(databricks_conn_id='databricsk_default')
        conn = hook.get_conn()
        workspace_url = (conn.host or '').rstrip('/')
        token = conn.password
        if not workspace_url or not token:
            raise ValueError("Databricks connection must have host and password (token)")
        factory = CloudFactory("databricks", databricks_workspace_url=workspace_url, databricks_token=token)
        compute = factory.get_compute(compute_type="databricks")
        payload = (
            {
                "cluster_name": "sample_cluster",
                "spark_version": "15.4.x-scala2.12",
                "node_type_id": "Standard_D4s_v3",
                "num_workers": 1,
                "autoscale": None,
                "driver_node_type_id": None,
                "runtime_engine": None,
                "data_security_mode": None,
                "single_user_name": None,
                "policy_id": None,
                "apply_policy_default_values": True,
                "idempotency_token": None,
                "aws_attributes": None,
                "azure_attributes": None,
                "gcp_attributes": None,
                "single_node": False,
                "autotermination_minutes": None,
                "enable_elastic_disk": True,
                "spark_conf": {},
                "spark_env_vars": {
                    "SECRET_MANAGER_PROVIDER": "databricks"
                },
                "custom_tags": {},
                "init_scripts": [
                    "/Workspace/Shared/bh-dev-utils/scripts/bh_databricks_grpc_server.sh"
                ],
                "libraries": [],
                "databricks_region": None,
                "bh_tags": []
            }
        )
        cluster_id = compute.create_compute(
            payload,
            compute_name=payload.get("cluster_name"),
            run_async=False,
        )
        if not cluster_id:
            raise ValueError("create_compute did not return cluster_id")
        return cluster_id

    create_compute_d2b5c2a85 = PythonOperator(
        task_id='create_compute_d2b5c2a85',
        python_callable=create_databricks_cluster_create_compute_d2b5c2a85,
        on_success_callback=common_task.success_callback,
        on_failure_callback=common_task.failure_callback,
    )


    from airflow.operators.python import PythonOperator
    end_flow_task = PythonOperator(
        task_id='end_flow_task',
        pre_execute=common_task.pre_execute_callback,
        python_callable=common_task.end_dag_task,
        on_success_callback=common_task.flow_success_callback,
        on_failure_callback=common_task.failure_callback,
    )

    start_flow_task >> create_compute_d2b5c2a85
    create_compute_d2b5c2a85 >> end_flow_task
