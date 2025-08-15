# Terraform variables for CVD AI Planogram Infrastructure

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "cvd-ai-planogram"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for deployment"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

# ECS Configuration
variable "app_desired_count" {
  description = "Desired number of app containers"
  type        = number
  default     = 2
}

variable "app_min_count" {
  description = "Minimum number of app containers for auto-scaling"
  type        = number
  default     = 2
}

variable "app_max_count" {
  description = "Maximum number of app containers for auto-scaling"
  type        = number
  default     = 10
}

variable "ai_desired_count" {
  description = "Desired number of AI service containers"
  type        = number
  default     = 2
}

variable "ai_min_count" {
  description = "Minimum number of AI service containers"
  type        = number
  default     = 1
}

variable "ai_max_count" {
  description = "Maximum number of AI service containers"
  type        = number
  default     = 5
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_storage_size" {
  description = "Database storage size in GB"
  type        = number
  default     = 100
}

variable "db_backup_retention_days" {
  description = "Database backup retention in days"
  type        = number
  default     = 7
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = false
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_node_count" {
  description = "Number of Redis nodes"
  type        = number
  default     = 1
}

# Application Configuration
variable "app_port" {
  description = "Application port"
  type        = number
  default     = 5000
}

variable "health_check_path" {
  description = "Health check endpoint path"
  type        = string
  default     = "/health"
}

# SSL Configuration
variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate in ACM"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

# Monitoring
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Cost Optimization
variable "use_spot_instances" {
  description = "Use Spot instances for non-critical workloads"
  type        = bool
  default     = false
}

variable "enable_auto_shutdown" {
  description = "Enable auto-shutdown for development environments"
  type        = bool
  default     = false
}

# Tags
variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Secrets ARNs (populated from AWS Secrets Manager)
variable "anthropic_api_key_arn" {
  description = "ARN of Anthropic API key in Secrets Manager"
  type        = string
  sensitive   = true
}

variable "session_secret_arn" {
  description = "ARN of session secret in Secrets Manager"
  type        = string
  sensitive   = true
}

# Locals for computed values
locals {
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  )
  
  environment_config = {
    dev = {
      instance_type     = "t3.small"
      autoscaling_min   = 1
      autoscaling_max   = 3
      db_instance_class = "db.t3.micro"
      redis_node_type   = "cache.t3.micro"
    }
    staging = {
      instance_type     = "t3.medium"
      autoscaling_min   = 2
      autoscaling_max   = 5
      db_instance_class = "db.t3.small"
      redis_node_type   = "cache.t3.small"
    }
    production = {
      instance_type     = "t3.large"
      autoscaling_min   = 3
      autoscaling_max   = 10
      db_instance_class = "db.r6g.xlarge"
      redis_node_type   = "cache.r6g.large"
    }
  }
}