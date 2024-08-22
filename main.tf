resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_vpc" "main_vpc" {
  cidr_block = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "fastapi-vpc-${random_id.suffix.hex}"
  }
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(aws_vpc.main_vpc.cidr_block, 8, 1)
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "public-subnet-1-${random_id.suffix.hex}"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(aws_vpc.main_vpc.cidr_block, 8, 2)
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "public-subnet-2-${random_id.suffix.hex}"
  }
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(aws_vpc.main_vpc.cidr_block, 8, 3)
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "private-subnet-1-${random_id.suffix.hex}"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = cidrsubnet(aws_vpc.main_vpc.cidr_block, 8, 4)
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "private-subnet-2-${random_id.suffix.hex}"
  }
}

resource "aws_internet_gateway" "main_gw" {
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    Name = "main-gw-${random_id.suffix.hex}"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_gw.id
  }

  tags = {
    Name = "public-route-table-${random_id.suffix.hex}"
  }
}

resource "aws_route_table_association" "public_subnet_1_association" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "public_subnet_2_association" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_security_group" "ecs_service_sg" {
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs-service-sg-${random_id.suffix.hex}"
  }
}

resource "aws_security_group" "lb_sg" {
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lb-sg-${random_id.suffix.hex}"
  }
}

resource "aws_security_group_rule" "allow_mysql_inbound" {
  type              = "ingress"
  from_port         = 3306
  to_port           = 3306
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"] # Replace with specific IPs for security
  security_group_id = aws_security_group.ecs_service_sg.id
}

resource "aws_ecs_cluster" "fastapi_cluster" {
  name = "${var.cluster_name}-${random_id.suffix.hex}"
}

resource "aws_ecr_repository" "fastapi_repo" {
  name = "fastapi-repo-${random_id.suffix.hex}"
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Attach ECS Task Execution Policy to Role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.ecs_task_execution_role.name
}

# Additional Policy Attachment Example (S3 Full Access)
resource "aws_iam_role_policy_attachment" "ecs_additional_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.ecs_task_execution_role.name
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/fastapi-${random_id.suffix.hex}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "fastapi_task" {
  family                   = "${var.task_name}-${random_id.suffix.hex}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # Increased CPU
  memory                   = "4096"  # Increased memory to 4GB
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name             = "fastapi-container"
    image            = "${aws_ecr_repository.fastapi_repo.repository_url}:latest"
    essential        = true
    memory           = 4096  # Increased memory to 4GB
    cpu              = 1024  # Increased CPU
    portMappings     = [{
      containerPort = 80
      hostPort      = 80
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/fastapi-${random_id.suffix.hex}"
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
    environment = [
      {
        name  = "DB_CLUSTER_ARN"
        value = aws_rds_cluster.fastapi_db_cluster.arn
      },
      {
        name  = "DB_SECRET_ARN"
        value = aws_secretsmanager_secret.db_secret.arn
      },
      {
        name  = "DB_DATABASE_NAME"
        value = var.rds_database_name
      },
      {
        name  = "S3_BUCKET_NAME"
        value = var.s3_bucket_name
      }
    ]
  }])
}

resource "aws_ecs_service" "fastapi_service" {
  name            = "${var.service_name}-${random_id.suffix.hex}"
  cluster         = aws_ecs_cluster.fastapi_cluster.id
  task_definition = aws_ecs_task_definition.fastapi_task.arn
  desired_count   = 2  # Adjust for high availability

  launch_type = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi_tg.arn
    container_name   = "fastapi-container"
    container_port   = 80
  }

  depends_on = [
    aws_lb_listener.fastapi_lb_listener
  ]
}

resource "aws_appautoscaling_target" "ecs_autoscaling_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.fastapi_cluster.name}/${aws_ecs_service.fastapi_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_autoscaling_policy_cpu" {
  name               = "ecs-autoscaling-cpu-${random_id.suffix.hex}"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.ecs_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_autoscaling_target.scalable_dimension
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 75.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_appautoscaling_policy" "ecs_autoscaling_policy_memory" {
  name               = "ecs-autoscaling-memory-${random_id.suffix.hex}"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.ecs_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_autoscaling_target.scalable_dimension
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 75.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_lb" "fastapi_lb" {
  name               = "fastapi-lb-${random_id.suffix.hex}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
}

resource "aws_lb_target_group" "fastapi_tg" {
  name     = "fastapi-tg-${random_id.suffix.hex}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main_vpc.id
  target_type = "ip"

  health_check {
    path                = "/"
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "fastapi_lb_listener" {
  load_balancer_arn = aws_lb.fastapi_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi_tg.arn
  }
}

resource "aws_rds_cluster" "fastapi_db_cluster" {
  cluster_identifier      = "${var.rds_cluster_identifier}-${random_id.suffix.hex}"
  engine                  = "aurora-mysql"
  engine_mode             = "serverless"
  database_name           = var.rds_database_name
  master_username         = var.db_username
  master_password         = var.db_password
  backup_retention_period = 7
  preferred_backup_window = "07:00-09:00"
  scaling_configuration {
    auto_pause             = true
    max_capacity           = 2
    min_capacity           = 1
    seconds_until_auto_pause = 300
  }
  vpc_security_group_ids = [aws_security_group.ecs_service_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  enable_http_endpoint   = true
  skip_final_snapshot    = true
}

resource "aws_iam_role" "rds_monitoring_role" {
  name = "rds-monitoring-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
  role       = aws_iam_role.rds_monitoring_role.name
}

resource "aws_db_subnet_group" "main" {
  name       = "main-subnet-group-${random_id.suffix.hex}"
  subnet_ids = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  tags = {
    Name = "Main subnet group"
  }
}

resource "aws_secretsmanager_secret" "db_secret" {
  name        = "fastapi-db-secret-${random_id.suffix.hex}"
  description = "RDS database credentials for FastAPI"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_username,
    password = var.db_password,
  })
}

# VPC Flow Logs for monitoring network traffic
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  name              = "/aws/vpc/flow-logs-${random_id.suffix.hex}"
  retention_in_days = 7
}

resource "aws_flow_log" "vpc_flow_logs" {
  vpc_id            = aws_vpc.main_vpc.id
  traffic_type      = "ALL"
  log_destination   = aws_cloudwatch_log_group.vpc_flow_logs.arn
  iam_role_arn      = aws_iam_role.flow_log_role.arn
}

resource "aws_iam_role" "flow_log_role" {
  name = "flow-log-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })

  # Attach an inline policy that gives the necessary permissions for flow logs
  inline_policy {
    name = "flow-logs-policy-${random_id.suffix.hex}"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Effect = "Allow",
          Action = [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          Resource = "*"
        }
      ]
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Alarms for ECS
resource "aws_cloudwatch_metric_alarm" "cpu_utilization_high" {
  alarm_name          = "fastapi-high-cpu-${random_id.suffix.hex}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"

  dimensions = {
    ClusterName = aws_ecs_cluster.fastapi_cluster.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn] # Notify via SNS
}

resource "aws_sns_topic" "alerts" {
  name = "fastapi-alerts-${random_id.suffix.hex}"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "osagie@medoid.tech"
}

