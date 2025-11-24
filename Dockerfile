FROM jenkins/jenkins:lts-jdk17

USER root

# Install docker + kubectl
RUN apt-get update && \
    apt-get install -y docker.io curl apt-transport-https ca-certificates gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key \
      | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" \
      > /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y kubectl && \
    rm -rf /var/lib/apt/lists/*

# Add jenkins user to docker group so it can talk to /var/run/docker.sock
RUN groupadd -g 999 docker || true && \
    usermod -aG docker jenkins

USER jenkins

