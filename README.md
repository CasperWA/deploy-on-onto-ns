# Deployment service for onto-ns.com

Deploy various software for the onto-ns.com website by using a simple REST API service.

## Run the service

First, download and install the Python package from GitHub:

```shell
# Download (git clone)
git clone https://github.com/CasperWA/deploy-on-onto-ns.git
cd deploy-on-onto-ns

# Install (using pip)
python -m pip install -U pip
pip install -U -e .
```

### Using Docker

For development, build and run the Deployment service for onto-ns.com Docker image:

```shell
docker build --pull -t deploy-on-onto-ns --target development .
docker run --rm -d \
  --name "deploy-on-onto-ns" \
  -p "8000:80" \
  --volume "$(pwd):/app" \
  deploy-on-onto-ns
```

Now, go to [localhost:8000/docs](http://localhost:8000/docs) and try it out.

---

For production follow the same instructions above for building and running the Deployment service for onto-ns.com Docker image, but exchange the `--target` value with `production`.

## Licensing & copyright

All files in this repository are [MIT licensed](LICENSE).  
Copyright by [Casper Welzel Andersen](https://github.com/CasperWA).

## Acknowledgements

This project is made possible by funding from:

- MEDIATE (2022-2025) that receives funding from the RCN, Norway, FNR, Luxembourg, and SMWK, Germany via the M-ERA.NET programme, project9557.
  M-ERA.NET 2 and M-ERA.NET 3 have received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreements No 685451 and No 958174.
- [MatCHMaker](https://he-matchmaker.eu) (2022-2026) that receives funding from the European Union’s Horizon Europe research and innovation programme under grant agreement No 101091687.
