# Openshift AI Deployments

## Pre-requisites
* See the <a href="https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.22/html/installing_and_uninstalling_openshift_ai_self-managed_in_a_disconnected_environment/deploying-openshift-ai-in-a-disconnected-environment_install#requirements-for-openshift-ai-self-managed_install" target="_blank">Openshift AI documentation</a>

## To deploy Openshift AI
1. Login to the Openshift cluster
```
source .env
oc login --token=$OC_TOKEN --server=$OC_SERVER
```
2. Create a cluster-admin user:
```
htpasswd -c -B -b $OC_HTPASSWD_FILE $OC_HTPASSWD_USER $OC_HTPASSWD_PASSWORD
oc create secret generic htpass-secret --from-file=htpasswd=$OC_HTPASSWD_FILE -n openshift-config
oc apply -f resources/oauth_htpasswd.yaml
oc adm groups new $OC_HTPASSWD_GROUP
oc adm groups add-users $OC_HTPASSWD_GROUP $OC_HTPASSWD_USER
oc adm policy add-cluster-role-to-group cluster-admin $OC_HTPASSWD_GROUP
```

3. Deploy Minio: (see <a href="https://ai-on-openshift.io/tools-and-applications/minio/minio/#log-on-to-your-project-in-openshift-console" target="_blank">link</a>)
```
oc new-project minio --display-name="Minio S3 for LLMs"
oc apply -f resources/minio/minio-all.yaml
```

4. Login as the newly created user (update OC_TOKEN in .env file first as 
appropriate):
```
source .env
oc login --token=$OC_TOKEN --server=$OC_SERVER
```

5. Create a **MachineSet** template with GPU instance-type **g6e.2xlarge** 
   (see resources/templates/machineset.yaml for an example)

6. Run the script / steps below (installs NFD Operator):
```
oc create -f resources/nfd/
```

7. Run the script / steps below (installs NFD Instance):
```
oc create -f resources/nfd-components/
oc get nodes -l "feature.node.kubernetes.io/pci-10de.present=true"
```

8. Run the script / steps below (installs NVIDIA GPU Operator):
```
NVIDIA_CHANNEL=$(oc get packagemanifest gpu-operator-certified -n openshift-marketplace -o jsonpath='{.status.defaultChannel}')
NVIDIA_CSV=$(oc get packagemanifests/gpu-operator-certified -n openshift-marketplace -ojson | jq -r '.status.channels[] | select(.name == "'$CHANNEL'") | .currentCSV')
INSTALL_PLAN=$(oc get installplan -n nvidia-gpu-operator -oname)
oc patch $INSTALL_PLAN -n nvidia-gpu-operator --type merge --patch '{"spec":{"approved":true }}'
envsubst < resources/templates/nvidiasubscription.yaml.in > resources/nvidia/subscription.yaml
oc create -f resources/nvidia/
oc get csv -n nvidia-gpu-operator ${NVIDIA_CSV} -ojsonpath={.metadata.annotations.alm-examples} |jq .[0] > clusterpolicy.json
oc apply -f clusterpolicy.json
oc get pods,daemonset -n nvidia-gpu-operator
```

9. Run the script / steps below (installs Openshift Serverless Operator):
```

```

10. Run the script / steps below (installs Openshift Service Mesh Operator):
```

```

11. Run the script below (installs Openshift AI Operator):
```
oc create -f resources/openshiftai/
```
12. Run the script below (installs Openshift AI Components):
```
oc create -f resources/openshiftai-components/
```

13. Set up monitoring:
```
# Monitoring Dashboard
curl -LfO https://github.com/NVIDIA/dcgm-exporter/raw/main/grafana/dcgm-exporter-dashboard.json
oc create configmap nvidia-dcgm-exporter-dashboard -n openshift-config-managed --from-file=dcgm-exporter-dashboard.json
oc label configmap nvidia-dcgm-exporter-dashboard -n openshift-config-managed "console.openshift.io/dashboard=true"
oc label configmap nvidia-dcgm-exporter-dashboard -n openshift-config-managed "console.openshift.io/odc-dashboard=true"

# NVIDIA GPU Operator Dashboard
helm repo add rh-ecosystem-edge https://rh-ecosystem-edge.github.io/console-plugin-nvidia-gpu
helm repo update
helm install -n nvidia-gpu-operator console-plugin-nvidia-gpu rh-ecosystem-edge/console-plugin-nvidia-gpu
oc get consoles.operator.openshift.io cluster --output=jsonpath="{.spec.plugins}"
```

14. Install Dev Spaces: (use <a href="https://github.com/settings/applications/new" 
target="_blank">DevSpaces documentation</a>)
```
source .env
export DEVSPACES_CLIENT_ID=$DEVSPACES_CLIENT_ID
export DEVSPACES_CLIENT_SECRET=$DEVSPACES_CLIENT_SECRET
oc create namespace openshift-devspaces
envsubst < resources/templates/devspacessecret.yaml.in > resources/devspaces/secret.yaml
oc apply -f resources/devspaces/secret.yaml
```

15. Install MySQL Instance:
```
oc new-project mysql
oc create secret generic mysql-root-pass --from-literal=password=$MYSQL_ROOT_PASSWORD -n mysql
oc create secret generic mysql-user-pass --from-literal=username=mysql --from-literal=password=$MYSQL_USER_PASSWORD -n mysql
oc apply -f resources/mysql -n mysql
oc expose deploy mysql-deployment -n mysql
oc expose svc mysql-deployment -n mysql
```

16. Install TrustyAI:
```

```

17. Install N8N: (Docs: https://community-charts.github.io/docs/charts/n8n/usage)
```
# As a pre-requisite, run the following commands if a customer docker image does not already exist (tested with 8GB RAM):
source .env
sudo dnf install container-tools
oc new-project n8n
oc create secret docker-registry quay-creds --docker-server=quay.io --docker-username=${DOCKER_USERNAME}${DOCKER_USERNAME_SUFFIX} --docker-password=${DOCKER_PASSWORD} --docker-email=${DOCKER_EMAIL}
oc new-build --name=n8n-custom --to="quay.io/oawofolurh/n8n:latest" --strategy=docker --push-secret quay-creds --binary
oc start-build n8n-custom --from-dir docker --follow

# Run the following to install N8N:
oc new-project n8n
helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update
oc apply -f resources/n8n/pvc.yaml -n n8n
oc apply -f resources/n8n/deployment.yaml -n n8n
oc adm policy add-scc-to-user anyuid -z n8n-workflows
oc expose svc n8n-workflows -n n8n
# Access the N8N UI: echo http://`oc get route -o json | jq -r '.items[0].spec.host'`
```
18. Install Airbyte: (Docs: https://docs.airbyte.com)
```
helm repo add airbyte https://airbytehq.github.io/helm-charts
helm repo update
oc new-project airbyte
helm install airbyte airbyte/airbyte
```
19. Install OpenWebUI:
oc new-project openwebui
helm repo add open-webui https://open-webui.github.io/helm-charts
helm repo update
helm install openwebui open-webui/open-webui

20. Set up MCP Server:

```

```

21. Install Postgres:
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
#brew install postgresql #for mac users
oc new-project postgresql
helm install my-postgresql bitnami/postgresql \
      --set postgresqlDatabase=demo \
      --set primary.persistence.size=10Gi
```

Test the installation:
```
export POSTGRES_PASSWORD=$(oc get secret my-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
oc port-forward --namespace postgresql svc/my-postgresql 5432:5432
PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U postgres -d postgres -p 5432
```

To uninstall:
```
helm install my-postgresql
oc delete pvc data-my-postgresql-0 -npostgresql
```

## To Build A Custom Workbench Image

1. Run this script:
```
source .env
cd docker
podman build -t quay.io/oawofolurh/agentic-wb:latest .
podman push quay.io/oawofolurh/agentic-wb:latest
cd -
```

OR

```
oc new-build --name=data-prep-wb --to="quay.io/oawofolurh/agentic-wb:latest" --strategy=docker --binary
oc start-build data-prep-wb --from-dir docker --follow
```

## To Deploy Custom Workbench
1. Use the image built above to import a new notebook image
	* Attach a GPU accelerator profile if one exists
    * For AnythingLLM: Use quay.io/rh-aiservices-bu/anythingllm-workbench
2. When creating the workbench in the Web GUI Console:
	* Use the following script to generate the **wb-secret.yaml** file to attach to the workbench:
	
	```
	oc create secret generic data-prep-wb --from-env-file .env
	oc get secret data-prep-wb -oyaml > resources/wb-secret.yaml
    ```
 
    For AnythingLLM:
    ```
	oc create secret generic anythingllm-wb --from-env-file resources/anythingllm/.env
	oc get secret anythingllm-wb -oyaml > resources/anythingllm/wb-secret.yaml
    
    ```
 
## Other
### Deploying LLMs with larger context lengths
1. Include the following configuration during deployment:
   ```
   args: --hf-overrides.max-position-embeddings=16000
   ```
   or
   ```
   args: --max-model-len=16000
        --hf-overrides.max_model_len=16000
        --enforce-eager
   env: VLLM_ALLOW_LONG_MAX_MODEL_LEN=1
   ```
2. .


### Deploying LLMs with custom dependencies (Method 1)
1. Deploy a custom serving runtime
   ```
   oc apply -f resources/custom-vllm-serving-runtime/custom-vllm.yaml
   ```
2. .

### Build ModelCar images
NOTES:
1. When pulling from a private registry, set up a secret with the appropriate
auth credentials and link it to the service account ("default" in the example 
below) for the deployment:
```
oc create secret docker-registry quay-creds --docker-server=quay.io --docker-username=${DOCKER_USERNAME}${DOCKER_USERNAME_SUFFIX} --docker-password=${DOCKER_PASSWORD} --docker-email=${DOCKER_EMAIL}
secret/quay-creds created
oc secrets link default quay-creds --for=pull
```