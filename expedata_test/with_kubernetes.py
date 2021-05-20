from kubernetes import client as k8s_client
from kubernetes import config
import os
import logging

# IP WARNING: most of the code of this file was **taken* from the 
# [KubeFlow project](https://github.com/kubeflow/pipelines) which is BAD !

class KubeCloud:

  def __init__(self):
    # From pipelines/sdk/python/kfp/containers/_k8s_job_helper.py
    k8s_config_file = os.environ.get('KUBECONFIG')
    if k8s_config_file:
      try:
        logging.info('Loading kubernetes config from the file %s', k8s_config_file)
        config.load_kube_config(config_file=k8s_config_file)
      except Exception as e:
        raise RuntimeError('Can not load kube config from the file %s, error: %s', k8s_config_file, e)
    else:
      try:
        config.load_incluster_config()
        logging.info('Initialized with in-cluster config.')
      except:
        logging.info('Cannot find in-cluster config, trying the local kubernetes config. ')
        try:
          config.load_kube_config()
          logging.info('Found local kubernetes config. Initialized with kube_config.')
        except:
          raise RuntimeError('Forgot to run the gcloud command? Check out the link: \
          https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl for more information')
    self._api_client = k8s_client.ApiClient()
    self._corev1 = k8s_client.CoreV1Api(self._api_client)

  def print_pods(self):
    # Running
    #   ret = self._corev1.list_pod_for_all_namespaces(watch=False)
    # fails with
    # HTTP response body: {
    #   "kind":"Status",
    #   "apiVersion":"v1",
    #   "metadata":{},
    #   "status":"Failure",
    #   "message":"pods is forbidden: User \"system:serviceaccount:my-airflow-namespace:my-airflow-cluster\" cannot list resource \"pods\" in API group \"\" at the cluster scope",
    #   "reason":"Forbidden",
    #   "details":{"kind":"pods"},
    #   "code":403
    # }
    #

    # Kubernetes: How do I get all pods in a namespace using the python api?
    # https://stackoverflow.com/questions/52329005/kubernetes-how-do-i-get-all-pods-in-a-namespace-using-the-python-api

    # How do I get the current namespace
    # https://github.com/kubernetes-client/python/issues/363

    # FIXME: won't work e.g. on OSX
    current_namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()
    pods = self._corev1.list_namespaced_pod(current_namespace).items
    print('Listing pods with their IPs:')
    for pod in pods:
      print("%s\t%s\t%s" % (pod.status.pod_ip,
                            pod.metadata.namespace,
                            pod.metadata.name))

def list_pods():
  KubeCloud().print_pods()

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

if __name__ == "__main__":
  k = KubeCloud()
  # k.print_pods() fails on mac
