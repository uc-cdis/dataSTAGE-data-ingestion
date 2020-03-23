fence-create link-external-bucket --bucket-name phs000920.c1
fence-create link-external-bucket --bucket-name phs000921.c2
fence-create link-bucket-to-project --bucket_id phs000920.c1 --bucket_provider google --project_auth_id phs000920.c1
fence-create link-bucket-to-project --bucket_id phs000921.c2 --bucket_provider google --project_auth_id phs000921.c2
fence-create link-bucket-to-project --bucket_id phs000920.c1 --bucket_provider google --project_auth_id admin
fence-create link-bucket-to-project --bucket_id phs000921.c2 --bucket_provider google --project_auth_id admin
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs000920.c1
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs000921.c2