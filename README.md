# 🩸 Painterest

Privacy-respecting, anonymous, NoJS-supporting Pinterest frontend.

## ✨ Features

- [ ] API
  - [x] Search
  - [ ] Retrieval of specific pins
    - [x] Basic information (name, description, image and tags)
    - [ ] Comments
  - [x] Image proxy
  - [ ] Search by tags

- [ ] Frontend
  - [ ] Homepage
  - [x] Search (NoJS)
  - [x] Search (JS/Infinite scroll)
  - [ ] Pins
    - [x] Regular pins
    - [x] Business pins
    - [ ] Video pins
    - [x] Pins from other sites
    - [ ] Comments

## 🚀 Deployment

Clone repository:

```sh
git clone https://codeberg.org/thirtysix/painterest.git
cd painterest
```

### 🐳 With Docker

```sh
docker build . -t painterest
docker compose up -d
```

### 💻 Without containerization

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
uvicorn src.main:app --no-access-log --proxy-headers --forwarded-allow-ips '*' --host 0.0.0.0 --port 8889
```

### 🛡️ Running behind a reverse proxy

To run the app behind a reverse proxy, ensure that the appropriate proxy headers are added.
Below is a sample configuration for NGINX:

```text
location / {
    proxy_pass http://127.0.0.1:8889;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 📄 Changelog

See [CHANGELOG.md](CHANGELOG.md) file.

## 🔧 Development

Install Rye by following
the [installation guide](https://rye.astral.sh/guide/installation/).

Use `rye sync` to install dependencies and required Python version.

Use `rye run dev` to start development server which will reload on every change to source code.

Use `rye check --fix` and `rye fmt` to lint and format code. Assumed to be run before each commit
to guarantee code quality.

Use `rye run basedpyright` to ensure typing is correct.

## 📜 License

This project is licensed under the AGPLv3+ license - see the [license file](LICENSE) for details.
