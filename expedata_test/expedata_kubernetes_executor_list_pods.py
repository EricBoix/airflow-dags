# IP warning
#
# This is a derived copy of file
# https://github.com/apache/airflow/blob/master/airflow/example_dags/example_kubernetes_executor.py
# of an airflow code... Refer to http://www.apache.org/licenses/LICENSE-2.0
# for original license and https://github.com/apache/airflow for original
# propriety thingies...
"""
This is an example dag for using the Kubernetes Executor.
"""
from airflow import DAG
from airflow.example_dags.libs.helper import print_stuff
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import os
import sys
# Otherwise the importation of with_kubernetes.py fails with ModuleNotFoundError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from .with_kubernetes import KubeCloud

args = {
    'owner': 'airflow',
}

with DAG(
    dag_id='expedata_kubernetes_executor_list_pods',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['expedata', 'test'],
) as dag:

    affinity = {
        'podAntiAffinity': {
            'requiredDuringSchedulingIgnoredDuringExecution': [
                {
                    'topologyKey': 'kubernetes.io/hostname',
                    'labelSelector': {
                        'matchExpressions': [{'key': 'app', 'operator': 'In', 'values': ['airflow']}]
                    },
                }
            ]
        }
    }

    tolerations = [{'key': 'dedicated', 'operator': 'Equal', 'value': 'airflow'}]

    def check_installed_libraries():
        """
        Checks which libraries are installed
        :raises SystemError: when some lib is not found
        """
        local_dir= os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("expedata_kubernetes_executor_list_pods.py: ", local_dir)
        print(os.listdir(local_dir))
        try:
          import kubernetes
        except:
            raise SystemError("Kubernetes library not found")

    def list_pods():
        """
        Connect directly (without making reference to airflow library
        and although this will be executed within a KubernetesOperator
        deployed by airflow) the k8s cloud and list the pods.
        """
        k = KubeCloud()
        k.print_pods()

    # You don't have to use any special KubernetesExecutor configuration if
    # you don't want to
    start_task = PythonOperator(
       task_id="start_task",
       python_callable=print_stuff
    )

    # But you can if you want to
    one_task = PythonOperator(
        task_id="one_task",
        python_callable=check_installed_libraries,
        executor_config={"KubernetesExecutor": {"image": "apache/airflow:2.0.2-python3.8"}},
    )

    # Check available libraries in airflow/ci:latest image
    two_task = PythonOperator(
        task_id="two_task",
        python_callable=list_pods,
        executor_config={"KubernetesExecutor": {"image": "apache/airflow:2.0.2-python3.8"}},
    )

    # Limit resources on this operator/task with node affinity & tolerations
    three_task = PythonOperator(
        task_id="three_task",
        python_callable=print_stuff,
        executor_config={
            "KubernetesExecutor": {
                "request_memory": "128Mi",
                "limit_memory": "128Mi",
                "tolerations": tolerations,
                "affinity": affinity,
            }
        },
    )

    # Add arbitrary labels to worker pods
    four_task = PythonOperator(
        task_id="four_task",
        python_callable=print_stuff,
        executor_config={"KubernetesExecutor": {"labels": {"foo": "bar"}}},
    )

    start_task >> [one_task, two_task, three_task, four_task]
