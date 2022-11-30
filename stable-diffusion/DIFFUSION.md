# Running Stable Diffusion V2 on Anyscale

In this example, we will deploy stable diffusion model on Anyscale using [Anyscale Production Services](https://docs.anyscale.com/user-guide/run-and-monitor/production-services)

## Preparing your local shell environment
Start by making sure anyscale is properly setup on your local machine. You only need to do it once.

```bash
pip install -U anyscale
anyscale auth set
```

The configuration required is in a GitHub repo, let's clone it.

```bash
git clone https://github.com/anyscale/docs_examples.git
cd docs_examples/stable-diffusion
```

Anyscale services is a managed Ray Cluster running on your infrastructure. To run it, we need the following setup:
* A cluster environment describing the container image and Python dependencies. You can learn more about it [here](https://docs.anyscale.com/user-guide/configure/dependency-management/anyscale-environments).
* A service spec describing the configuration for the size of cluster (number of nodes) and the entrypoint to your code. You can learn more about it [here](https://docs.anyscale.com/user-guide/run-and-monitor/production-services).
* The code that host the model. The code is written to [Ray Serve](https://rayserve.org) framework to enable seamless scaling for your ML model in production.

## Building the cluster environment
We will start by building the cluster environment. In particular, we will be specifying a list of `pip` dependencies to be installed on top of Anyscale base machine learning image.

The following command will take about 10-20 minutes because it is installing and packaging the [diffusers](https://github.com/huggingface/diffusers) library and re-installing PyTorch. You only need to do it once.

```bash
$ anyscale cluster-env build cluster_env.yaml --name stable-diffusion-env

Authenticating
Loaded Anyscale authentication token from ~/.anyscale/credentials.json.

Output
(anyscale +0.5s) Creating new cluster environment stable-diffusion-env
(anyscale +1.0s) Waiting for cluster environment to build. View progress at https://console.anyscale.com/configurations/app-config-details/bld_ciaf8xxdw5ly43ljkl6btmrk9x.
(anyscale +1.0s) status: pending
(anyscale +16.0s) status: pending
(anyscale +31.1s) status: in_progress
...
(anyscale +17m58.4s) status: in_progress
(anyscale +17m58.6s) Cluster environment successfully finished building.
```

You can take a look at the [`cluster_env.yaml`](./cluster_env.yaml) to see which packages we installed.

## Deploying the service
Once the environment is built, you can run the following command to deploy a running service on Anyscale.

```bash
$ anyscale service deploy service.yaml
Authenticating
Loaded Anyscale authentication token from ~/.anyscale/credentials.json.

Output
(anyscale +1.3s) No cloud or compute config specified, using the default: cpt_cbajad48yc8pi149wi9tai1e4j.
(anyscale +1.4s) No project specified. Continuing without a project.
(anyscale +2.2s) Maximum uptime is disabled for clusters launched by this service.
(anyscale +2.2s) Service service_wp5ygyetu3sn6s1bulp92ypr has been deployed. Current state of service: PENDING.
(anyscale +2.2s) Query the status of the service with `anyscale service list --service-id service_wp5ygyetu3sn6s1bulp92ypr`.
(anyscale +2.2s) View the service in the UI at https://console.anyscale.com/services/service_wp5ygyetu3sn6s1bulp92ypr.
```

You can take a look at the [`service.yaml`](./service.yaml) to see what we just deployed. You can also take a look at the [`service_aws.yaml`](./service_aws.yaml) or [`service_gcp.yaml`](./service_gcp.yaml) which adds more configuration to select their instance types. In Anyscale, you can directly select the type of instances the cloud provider offers.

While the service will take sometimes to start, let us explain the configuration items:

```
cluster_env: stable-diffusion-env
```
This specifies the base environment for the cluster to use. This is the image we just built. The environment image is versioned and you can pin it to a specific version. You can also overlay [runtime environment](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html) to your Ray application to allow different Python dependencies for different models in the same cluster.

```
runtime_env:
  working_dir: "https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip"
```
This specifies the code repository to be used for our application. Anyscale also supports private repo and [local directory upload](https://docs.anyscale.com/user-guide/configure/dependency-management/runtime-env-jobs-services). We recommend use a git url for reproducibility.

```
entrypoint: "cd stable-diffusion && serve run --non-blocking app:entrypoint"
```
This specifies how does Anyscale starts your service. We will use the `serve run` command to deploy the application in [`app.py`](./app.py). The application has two component: a FastAPI application validates and handle requests and a StableDiffusion deployment that auto-scale between 0 and 2 replicas.

```
healthcheck_url: "/-/healthz"
```
Anyscale services will actively health check your endpoint. You can specify a custom endpoint in your Ray Serve application, but here we just use the default one. If the service is done, Anyscale will restarts your cluster to attempt to make sure your application is healthy again.

```
access: "public"
```
Anyscale services are secured with different method of network authentication. By specifying `access: "public"`, your service is publicly available and guarded by an API token.


## Invoking the service
Let's navigate to the service page. You can find the link in the logs of the `anyscale service deploy` command. Something like:

```
(anyscale +2.9s) View the service in the UI at https://console.anyscale.com/services/service_gxr3cfmqn2gethuuiusv2zif.
```

We will now test the service by invoking it through the web interface. You can also call the service programmatically (see the instruction from top right corner's Query button).

<img width="800" alt="image" src="https://user-images.githubusercontent.com/21118851/204908984-d349c214-dbf7-4719-9640-6206df30ca1f.png">

1. Wait for the service to be in a "Running" state.
2. In the "Deployments" section, find the "APIIngress" row, click the "View" under "API Docs".
3. You should now see a OpenAPI rendered documentation page.
4. Click the `/imagine` endpoint, then "Try it out" to enable calling it via the interactive API browser.
5. Fill in your prompt and click execute.

Because the diffusion model scales to zero, the first "cold start" invocation will be slow. Anyscale will bring up a GPU node and deploys the model there. You can observe the cold start process by going into the cluster page (in service page, under "Resource Usage", and under "Cluster").

<img width="800" alt="image" src="https://user-images.githubusercontent.com/21118851/204909023-9e3fac37-40c0-44e3-bfe0-4db502e30c2e.png">

Once you are in the cluster page, you can observe the status via "Autoscaler status log". It typically takes 5 to 8 minutes for a GPU node to be ready. You can also click "Dashboard" in the cluster page to observe the current node and process status.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/21118851/204909096-ff0d2b7b-ceac-44db-bb06-30ba1ae59873.png">


After the GPU node is up and model deployed, the execute call should go through and inference should be performed.

Here's what a successful run should look like:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/21118851/204908845-538875a5-9f67-487a-860d-26bc81257d9a.png">

## Known Issue
If you are on GCP, the network times out after 15s, we are aware of this issue and working on a fix forward. You can workaround by:
- Retrying the requests once the node is up.
- Lower the image size for faster inference.
- Setup a custom load balancer in your infrastructure directly pointed to the Ray Cluster. (We can help you with this, please contact your Anyscale support team).
