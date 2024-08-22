output "ecs_cluster_name" {
  value = aws_ecs_cluster.fastapi_cluster.name
}

output "ecs_service_name" {
  value = aws_ecs_service.fastapi_service.name
}

output "load_balancer_dns" {
  value = aws_lb.fastapi_lb.dns_name
}

output "rds_cluster_endpoint" {
  value = aws_rds_cluster.fastapi_db_cluster.endpoint
}

