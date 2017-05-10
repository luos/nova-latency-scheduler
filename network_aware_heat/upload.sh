
#!/usr/bin/env bash
set -e -x
ssh -i ~/.ssh/lajos_gerecs_1 152.66.245.141  -p 2218 -l ubuntu "rm -rf ~/latency_scheduler/heat || true"
ssh -i ~/.ssh/lajos_gerecs_1 152.66.245.141  -p 2218 -l ubuntu "mkdir -p ~/latency_scheduler/heat || true"
scp -r -P 2218 ./* ubuntu@152.66.245.141:~/latency_scheduler/heat/
ssh -i ~/.ssh/lajos_gerecs_1 152.66.245.141  -p 2218 -l ubuntu "sudo service heat-engine restart"
