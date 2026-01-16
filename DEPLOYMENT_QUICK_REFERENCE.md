# Quick Reference: Deployment Configuration

## Command Syntax

```bash
cicd init [PATH] [OPTIONS]
```

## New Options

| Option | Short | Values | Default | Description |
|--------|-------|--------|---------|-------------|
| `--cloud-provider` | `-cp` | `local`, `aws`, `azure`, `gcp` | `local` | Cloud platform for deployment |
| `--deployment-type` | `-dt` | `webapp`, `instance` | `webapp` | Type of deployment target |

## Common Use Cases

### Local Development
```bash
cicd init
# or explicitly:
cicd init --cloud-provider local --deployment-type webapp
```

### AWS Web Application
```bash
cicd init --cloud-provider aws --deployment-type webapp
```
Best for: REST APIs, Web Services, Microservices  
AWS Services: Elastic Beanstalk, ECS, App Runner, ECR

### AWS VM Instance
```bash
cicd init --cloud-provider aws --deployment-type instance
```
Best for: Legacy apps, Custom configurations, Long-running services  
AWS Services: EC2, ECR

### Azure Web Application
```bash
cicd init --cloud-provider azure --deployment-type webapp
```
Best for: .NET apps, Node.js services, Container apps  
Azure Services: App Service, Container Instances, ACR

### Azure VM Instance
```bash
cicd init --cloud-provider azure --deployment-type instance
```
Best for: Windows apps, Custom VMs, Specialized workloads  
Azure Services: Virtual Machines, ACR

### Google Cloud Web Application
```bash
cicd init --cloud-provider gcp --deployment-type webapp
```
Best for: Containerized apps, Scalable services, Modern architectures  
GCP Services: Cloud Run, App Engine, GCR

### Google Cloud VM Instance
```bash
cicd init --cloud-provider gcp --deployment-type instance
```
Best for: Custom VMs, Persistent workloads, Specialized configurations  
GCP Services: Compute Engine, GCR

## Combining with Other Options

### Multiple CI/CD Platforms
```bash
cicd init --cloud-provider aws --platforms jenkins,gitlab,github
```

### Force Specific Framework
```bash
cicd init --framework python --cloud-provider azure --deployment-type webapp
```

### All Options Together
```bash
cicd init /path/to/project \
  --framework python \
  --platforms jenkins,gitlab \
  --cloud-provider aws \
  --deployment-type webapp
```

## Decision Tree

```
Choose Cloud Provider:
├── Local Development → --cloud-provider local
├── Amazon Web Services → --cloud-provider aws
├── Microsoft Azure → --cloud-provider azure
└── Google Cloud → --cloud-provider gcp

Choose Deployment Type:
├── Web Application/Service → --deployment-type webapp
│   ✓ Has HTTP endpoints
│   ✓ Needs autoscaling
│   ✓ Managed platform preferred
│
└── VM/Container Instance → --deployment-type instance
    ✓ Long-running processes
    ✓ Custom OS requirements
    ✓ Full VM control needed
```

## Template Variables Available

When creating custom templates, these variables are now available:

```jinja2
{{ cloud_provider }}    # 'local', 'aws', 'azure', 'gcp'
{{ deployment_type }}   # 'webapp', 'instance'
```

Example usage in templates:
```jinja2
{% if cloud_provider == 'aws' %}
  # AWS-specific configuration
  AWS_REGION: us-east-1
{% elif cloud_provider == 'azure' %}
  # Azure-specific configuration
  AZURE_REGION: eastus
{% endif %}

{% if deployment_type == 'webapp' %}
  # Web app optimizations
  ENABLE_AUTOSCALING: true
{% else %}
  # Instance configurations
  VM_SIZE: standard
{% endif %}
```

## Error Messages

### Invalid Cloud Provider
```
✗ Invalid cloud provider: invalid
Valid cloud providers: local, aws, azure, gcp
```

### Invalid Deployment Type
```
✗ Invalid deployment type: container
Valid deployment types: webapp, instance
```

## Help Command

For complete documentation:
```bash
cicd init --help
```

---

**Tip**: Start with `local` for development, then specify your cloud provider when ready to deploy!
