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
    ret = self._corev1.list_pod_for_all_namespaces(watch=False)
    logging.info('Listing pods with their IPs:')
    for i in ret.items:
      print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

if __name__ == "__main__":
  k = KubeCloud()
  k.print_pods()