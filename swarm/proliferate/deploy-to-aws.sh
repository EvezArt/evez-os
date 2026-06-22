#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# EVEZ Swarm — Deploy to AWS Free Tier
# Provisions 5 EC2 instances (t2.micro free tier), each running EVEZ
#
# Prerequisites: AWS CLI installed and configured
# Usage: ./deploy-to-aws.sh [region]
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

REGION="${1:-us-east-1}"
NODE_COUNT=5
INSTANCE_TYPE="t2.micro"
AMI="ami-0c7217cdde317cfec"  # Debian 12 in us-east-1
KEY_NAME="${2:-evez-swarm-key}"
SG_NAME="evez-swarm-sg"

echo "╔══════════════════════════════════════════════════╗"
echo "║     EVEZ SWARM → AWS DEPLOYMENT                  ║"
echo "║  Region:  ${REGION}"
echo "║  Nodes:   ${NODE_COUNT}"
echo "║  Type:    ${INSTANCE_TYPE} (free tier)"
echo "╚══════════════════════════════════════════════════╝"

# ─── Create Security Group ──────────────────────────────────────
echo "🛡️  Creating security group..."
SG_ID=$(aws ec2 create-security-group \
  --group-name ${SG_NAME} \
  --description "EVEZ Swarm Node" \
  --region ${REGION} 2>/dev/null || \
  aws ec2 describe-security-groups \
    --group-names ${SG_NAME} \
    --region ${REGION} \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp --port 7777 --cidr 0.0.0.0/0 \
  --region ${REGION} 2>/dev/null || true
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol udp --port 7778 --cidr 0.0.0.0/0 \
  --region ${REGION} 2>/dev/null || true
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp --port 7779 --cidr 0.0.0.0/0 \
  --region ${REGION} 2>/dev/null || true
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp --port 22 --cidr 0.0.0.0/0 \
  --region ${REGION} 2>/dev/null || true

echo "  ✅ Security group: ${SG_ID}"

# ─── Create Key Pair ────────────────────────────────────────────
echo "🔑 Ensuring key pair..."
aws ec2 create-key-pair \
  --key-name ${KEY_NAME} \
  --query 'KeyMaterial' \
  --output text \
  --region ${REGION} > ~/.ssh/${KEY_NAME}.pem 2>/dev/null || echo "  Key already exists"
chmod 600 ~/.ssh/${KEY_NAME}.pem 2>/dev/null || true

# ─── User Data Script ───────────────────────────────────────────
USER_DATA=$(cat <<'UD_EOF'
#!/bin/bash
apt-get update && apt-get install -y curl
curl -fsSL https://get.docker.com | sh
docker pull evez/node:latest
docker run -d --name evez-node \
  -p 7777:7777 -p 7778:7778/udp -p 7779:7779 \
  -v /opt/evez/data:/evez/data \
  -v /opt/evez/spine:/evez/spine \
  --restart unless-stopped \
  evez/node:latest
UD_EOF
)

# ─── Launch Instances ────────────────────────────────────────────
FIRST_IP=""

for i in $(seq 1 ${NODE_COUNT}); do
  NODE_NAME="evez-node-${i}"
  echo ""
  echo "🧠 Launching node ${i}/${NODE_COUNT}: ${NODE_NAME}"

  INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ${AMI} \
    --instance-type ${INSTANCE_TYPE} \
    --key-name ${KEY_NAME} \
    --security-group-ids ${SG_ID} \
    --user-data "${USER_DATA}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${NODE_NAME}},{Key=EVEZ,Value=swarm-node}]" \
    --region ${REGION} \
    --query 'Instances[0].InstanceId' \
    --output text)

  echo "  Instance: ${INSTANCE_ID}"

  # Wait for IP
  sleep 10
  IP=$(aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --region ${REGION} \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text 2>/dev/null || echo "pending")

  if [ ${i} -eq 1 ]; then
    FIRST_IP="${IP}"
  fi

  echo "  ✅ ${NODE_NAME} → ${IP}"
done

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  EVEZ SWARM DEPLOYED TO AWS                     ║"
echo "║  Bootstrap node: ${FIRST_IP}:7777"
echo "║  Total nodes: ${NODE_COUNT}"
echo "╚══════════════════════════════════════════════════╝"
