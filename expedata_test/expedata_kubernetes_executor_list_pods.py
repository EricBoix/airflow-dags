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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from with_kubernetes import KubeCloud
# FIXME: remove definitions of check_instaled_libraries and import as follows
# from with_kubernetes import KubeCloud, check_installed_libraries

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
        Checks whether required libraries are installed
        :raises SystemError: when some lib is not found
        """
        try:
          import kubernetes
        except:
            raise SystemError("Kubernetes library not found")
        print("Kubernetes python wrappers available.")
        return True

    def list_pods():
        """
        Connect directly (without making reference to airflow library
        and although this will be executed within a KubernetesOperator
        deployed by airflow) the k8s cloud and list the pods.
        """
        k = KubeCloud()
        k.print_pods()

    # You don't have to specify any special KubernetesExecutor configuration if
    # you don't want/need to
    start_task = PythonOperator(
       task_id="start_task",
       python_callable=print_stuff
    )

    # The following PythonOperator asserts that some libraries required by this workflow
    # are indeed avaible/offered by the prescribed image.
    one_task = PythonOperator(
        task_id="one_task",
        python_callable=check_installed_libraries,
        executor_config={"KubernetesExecutor": {"image": "apache/airflow:2.0.2-python3.8"}},
    )

    # List the pods encountered in the current namespace
    two_task = PythonOperator(
        task_id="two_task",
        python_callable=list_pods,
        executor_config={"KubernetesExecutor": {"image": "apache/airflow:2.0.2-python3.8"}},
    )

    # Dummy ending taask just to make sure the previous task ended cleanly.
    end_task = PythonOperator(
       task_id="end_task",
       python_callable=print_stuff
    )

    start_task >> one_task >> two_task >> end_task
