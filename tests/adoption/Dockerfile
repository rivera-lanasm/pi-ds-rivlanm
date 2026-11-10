# Adoption test: a fresh machine with pi, then ADOPT.md followed verbatim.
# Build from the repo root:
#   docker build -f tests/adoption/Dockerfile -t pi-harness-adoption .
#   docker run --rm pi-harness-adoption
FROM node:22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ripgrep curl ca-certificates jq \
 && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

RUN npm install -g @earendil-works/pi-coding-agent

# Repo snapshot, committed inside the image so `git clone` works.
# The real repo's commit state is untouched.
COPY . /src/pi-harness
RUN cd /src/pi-harness \
 && git init -q \
 && git add -A \
 && git -c user.email=test@example.com -c user.name=test commit -qm snapshot

COPY tests/adoption/run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
