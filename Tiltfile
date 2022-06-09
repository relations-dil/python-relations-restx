
docker_build('python-relations-restx-api', '.')

k8s_yaml(kustomize('kubernetes/tilt'))

k8s_resource('api', port_forwards=['8288:80', '18288:5678'])
