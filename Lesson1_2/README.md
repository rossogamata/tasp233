# 🛡️ AWS Basics: VPC · EC2 · Network ACL · Elastic IP
### Методології автоматизованого розгортання ІТ інфраструктури | Cloud Technologies Lab — 5-й курс / 5th Year

> **Середовище / Environment:** AWS Academy Learner Lab (CloudShell)
> **Тривалість / Duration:** ~120 хвилин / minutes
> **Інструмент / Tool:** AWS CLI via browser (CloudShell)

---

## 📋 Цілі заняття / Learning Objectives

| # | 🇺🇦 Українська | 🇬🇧 English |
|---|---|---|
| 1 | Користуватись **AWS CLI** через браузер | Use **AWS CLI** via browser (CloudShell) |
| 2 | Створити та налаштувати **VPC** | Create and configure a **VPC** |
| 3 | Розгорнути **EC2-інстанси** у різних підмережах | Deploy **EC2 instances** across subnets |
| 4 | Налаштувати **Network ACL** | Configure **Network ACL** rules |
| 5 | Створити та перемістити **Elastic IP** | Create and migrate an **Elastic IP** |

---

## 🗺️ Архітектура / Target Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  VPC: 10.0.0.0/16  (academy-vpc)                             │
│                                                              │
│  ┌───────────────────────┐    ┌───────────────────────────┐  │
│  │  Subnet-A             │    │  Subnet-B                 │  │
│  │  10.0.1.0/24          │    │  10.0.2.0/24              │  │
│  │  us-east-1a           │    │  us-east-1b               │  │
│  │                       │    │                           │  │
│  │  ┌─────────────────┐  │    │  ┌─────────────────────┐  │  │
│  │  │ EC2: WebServer  │  │    │  │  EC2: AppServer     │  │  │
│  │  │ ← EIP (step 8)  │──┼────┼──┼──→ EIP (step 9)     │  │  │
│  │  └─────────────────┘  │    │  └─────────────────────┘  │  │
│  └───────────────────────┘    └───────────────────────────┘  │
│                                                              │
│  [Internet Gateway]   [Route Table]   [Network ACL]          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Крок 0 — Запуск AWS CloudShell / Step 0 — Launch CloudShell

**🇺🇦** CloudShell — вбудований браузерний термінал AWS з попередньо налаштованим AWS CLI та правами вашого акаунту. Не потрібно вводити ключі доступу вручну.

**🇬🇧** CloudShell is a browser-based terminal built into the AWS Console. It comes pre-configured with AWS CLI and your account credentials — no manual key setup required.

### Кроки / Steps:
1. Увійдіть на [awsacademy.instructure.com](https://awsacademy.instructure.com) → **Learner Lab**
2. Натисніть **Start Lab** → дочекайтесь ● зеленого / Wait for ● green indicator
3. Натисніть **AWS** → відкриється AWS Console / Click **AWS** → Console opens
4. Клікніть іконку `>_` **CloudShell** у верхній панелі / Click `>_` in the top bar
5. Зачекайте ~30 сек ініціалізації / Wait ~30 sec for initialization

### ✅ Перевірка доступу / Verify access:

```bash
# Перевіряємо версію AWS CLI
# Checks the installed AWS CLI version
aws --version

# Перевіряємо поточну ідентичність (хто ми в AWS)
# Returns the identity tied to the current credentials
aws sts get-caller-identity
```

**Очікуваний результат / Expected output:**
```json
{
    "UserId": "AROA...",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/..."
}
```

---

## 🏗️ Крок 1 — Створення VPC / Step 1 — Create VPC

**🇺🇦** VPC (Virtual Private Cloud) — ізольована приватна мережа у хмарі AWS. Аналогія: ваша власна кімната у хмарному дата-центрі, де ніхто інший не має доступу.

**🇬🇧** VPC (Virtual Private Cloud) is your own isolated network within AWS. Think of it as a private room in the cloud data center — logically separated from all other tenants.

```bash
# aws ec2 create-vpc
#   --cidr-block 10.0.0.0/16
#       🇺🇦 Діапазон IP-адрес вашої мережі. /16 = 65 536 адрес (10.0.0.0–10.0.255.255)
#       🇬🇧 The IP address range for your network. /16 = 65,536 addresses
#
#   --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=academy-vpc}]'
#       🇺🇦 Додаємо мітку Name=academy-vpc для відображення у консолі
#       🇬🇧 Adds a Name tag so the resource is identifiable in the console
#
#   --query 'Vpc.VpcId'
#       🇺🇦 З відповіді (великий JSON) витягуємо тільки поле VpcId
#       🇬🇧 From the full JSON response, extract only the VpcId field
#
#   --output text
#       🇺🇦 Виводимо як простий рядок, не JSON — щоб зберегти у змінну
#       🇬🇧 Output as plain text instead of JSON — needed to save into a variable

VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=academy-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "✅ VPC створено / VPC created: $VPC_ID"
```

```bash
# aws ec2 modify-vpc-attribute
#   --vpc-id $VPC_ID
#       🇺🇦 ID VPC яку змінюємо (підставляємо зі змінної)
#       🇬🇧 The VPC to modify (substituted from our variable)
#
#   --enable-dns-hostnames '{"Value":true}'
#       🇺🇦 Дозволяє AWS автоматично призначати DNS-імена інстансам
#           (наприклад: ec2-1-2-3-4.compute-1.amazonaws.com)
#       🇬🇧 Allows AWS to auto-assign DNS names to instances
#           (e.g. ec2-1-2-3-4.compute-1.amazonaws.com)

aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames '{"Value":true}'

echo "✅ DNS hostnames увімкнено / DNS hostnames enabled"
```

> 💡 **CIDR /16 vs /24:** `/16` дає 65 536 адрес для всієї VPC. Підмережі будуть `/24` (256 адрес кожна) — підблок всередині `/16`. / `/16` gives 65,536 addresses for the whole VPC. Subnets use `/24` (256 addresses each) — a sub-block within the `/16`.

---

## 🌐 Крок 2 — Internet Gateway / Step 2 — Create Internet Gateway

**🇺🇦** Internet Gateway (IGW) — компонент що з'єднує VPC з публічним інтернетом. Без нього VPC повністю ізольована. IGW горизонтально масштабується і ніколи не є вузьким місцем.

**🇬🇧** Internet Gateway connects your VPC to the public internet. Without it, the VPC is fully isolated. The IGW is horizontally scaled and never becomes a bottleneck.

```bash
# aws ec2 create-internet-gateway
#   --tag-specifications '...'
#       🇺🇦 Мітка Name=academy-igw для зручності
#       🇬🇧 Name tag for easy identification
#
#   --query 'InternetGateway.InternetGatewayId'
#       🇺🇦 Витягуємо ID шлюзу з JSON-відповіді
#       🇬🇧 Extract the gateway ID from the JSON response

IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=academy-igw}]' \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

echo "✅ IGW створено / IGW created: $IGW_ID"
```

```bash
# aws ec2 attach-internet-gateway
#   --internet-gateway-id $IGW_ID
#       🇺🇦 IGW який прикріплюємо (щойно створений)
#       🇬🇧 The gateway to attach (just created above)
#
#   --vpc-id $VPC_ID
#       🇺🇦 VPC до якої прикріплюємо — один IGW на одну VPC
#       🇬🇧 The target VPC — one IGW per VPC is the limit

aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID

echo "✅ IGW прикріплено до VPC / IGW attached to VPC"
```

---

## 📦 Крок 3 — Підмережі / Step 3 — Create Subnets

**🇺🇦** Subnet — підмережа всередині VPC. Кожна підмережа розміщується в окремій **Availability Zone (AZ)** — фізично ізольованому дата-центрі. Розподіл по AZ забезпечує відмовостійкість.

**🇬🇧** A subnet is a segment of your VPC. Each subnet lives in a separate **Availability Zone (AZ)** — a physically isolated data center. Distributing across AZs provides fault tolerance.

```bash
# Підмережа A / Subnet A — us-east-1a
#
# aws ec2 create-subnet
#   --vpc-id $VPC_ID
#       🇺🇦 VPC до якої належить підмережа
#       🇬🇧 The parent VPC this subnet belongs to
#
#   --cidr-block 10.0.1.0/24
#       🇺🇦 Діапазон IP для цієї підмережі: 10.0.1.0–10.0.1.255
#           /24 дає 256 адрес (254 використовуваних — 2 резервує AWS)
#       🇬🇧 IP range for this subnet: 10.0.1.0–10.0.1.255
#           /24 gives 256 addresses (254 usable — 2 reserved by AWS)
#
#   --availability-zone us-east-1a
#       🇺🇦 Фізична зона розміщення (конкретний дата-центр у регіоні)
#       🇬🇧 Physical location (a specific data center within the region)

SUBNET_A_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=academy-subnet-a}]' \
  --query 'Subnet.SubnetId' \
  --output text)

echo "✅ Subnet-A створено / created: $SUBNET_A_ID"
```

```bash
# Підмережа B / Subnet B — us-east-1b (інша зона! / different AZ!)

SUBNET_B_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=academy-subnet-b}]' \
  --query 'Subnet.SubnetId' \
  --output text)

echo "✅ Subnet-B створено / created: $SUBNET_B_ID"
```

```bash
# aws ec2 modify-subnet-attribute
#   --subnet-id $SUBNET_A_ID
#       🇺🇦 Яку підмережу змінюємо
#       🇬🇧 Which subnet to modify
#
#   --map-public-ip-on-launch
#       🇺🇦 Кожен новий інстанс у цій підмережі автоматично отримає публічний IP
#           Без цього прапорця інстанс матиме тільки приватний IP
#       🇬🇧 Each new instance in this subnet automatically gets a public IP
#           Without this flag, the instance would only have a private IP

aws ec2 modify-subnet-attribute \
  --subnet-id $SUBNET_A_ID \
  --map-public-ip-on-launch

aws ec2 modify-subnet-attribute \
  --subnet-id $SUBNET_B_ID \
  --map-public-ip-on-launch

echo "✅ Auto-assign Public IP увімкнено / enabled"
```

---

## 🛣️ Крок 4 — Таблиця маршрутів / Step 4 — Route Table

**🇺🇦** Route Table — набір правил що визначають куди направляти мережеві пакети. Без маршруту `0.0.0.0/0 → IGW` підмережа є приватною і не має виходу в інтернет.

**🇬🇧** A Route Table is a set of rules that determine where network packets are sent. Without a `0.0.0.0/0 → IGW` route, the subnet is private with no internet access.

```bash
# aws ec2 create-route-table
#   --vpc-id $VPC_ID
#       🇺🇦 VPC для якої створюємо таблицю маршрутів
#       🇬🇧 The VPC this route table belongs to
#
#   --query 'RouteTable.RouteTableId'
#       🇺🇦 Витягуємо ID таблиці для подальшого використання
#       🇬🇧 Extract the table ID for later use

RT_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=academy-rt-public}]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

echo "✅ Route Table створено / created: $RT_ID"
```

```bash
# aws ec2 create-route
#   --route-table-id $RT_ID
#       🇺🇦 До якої таблиці додаємо маршрут
#       🇬🇧 The route table to add the route to
#
#   --destination-cidr-block 0.0.0.0/0
#       🇺🇦 "Будь-яка IP-адреса" — маршрут за замовчуванням (default route)
#           Якщо жоден конкретніший маршрут не підходить — трафік іде сюди
#       🇬🇧 "Any IP address" — the default route
#           If no more specific route matches, traffic follows this rule
#
#   --gateway-id $IGW_ID
#       🇺🇦 Трафік до "будь-якої адреси" направляємо через Internet Gateway
#       🇬🇧 Send traffic destined for "any address" through the Internet Gateway

aws ec2 create-route \
  --route-table-id $RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

echo "✅ Default route → IGW додано / added"
```

```bash
# aws ec2 associate-route-table
#   🇺🇦 Прив'язуємо таблицю маршрутів до підмереж.
#       Без цього підмережа використовує "main route table" VPC (без IGW)
#   🇬🇧 Associate the route table with the subnets.
#       Without this, subnets use the VPC "main route table" (which has no IGW route)

aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_A_ID
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_B_ID

echo "✅ Route Table прив'язано до підмереж / associated with both subnets"
```

---

## 🔒 Крок 5 — Network ACL / Step 5 — Network ACL

**🇺🇦** Network ACL (NACL) — перший рівень захисту на рівні **підмережі**. Є **stateless**: кожен пакет перевіряється окремо, включно з відповідями. Правила перевіряються від меншого номера — перше співпадіння застосовується.

**🇬🇧** Network ACL is the first line of defense at the **subnet** level. It is **stateless**: every packet (including responses) is evaluated independently. Rules are checked from lowest number — the first match is applied.

> | | 🇺🇦 Network ACL | 🇺🇦 Security Group |
> |---|---|---|
> | **Рівень** | Підмережа | Інстанс |
> | **Стан** | Stateless | Stateful |
> | **Правила** | Allow + Deny | Тільки Allow |
> | **Порядок** | № правила (↑ пріоритет) | Всі перевіряються |
>
> | | 🇬🇧 Network ACL | 🇬🇧 Security Group |
> |---|---|---|
> | **Level** | Subnet | Instance |
> | **State** | Stateless | Stateful |
> | **Rules** | Allow + Deny | Allow only |
> | **Order** | Rule # (lower = higher priority) | All evaluated |

```bash
# Отримуємо ID стандартного NACL нашої VPC
# Get the default NACL that was automatically created with the VPC

# aws ec2 describe-network-acls
#   --filters "Name=vpc-id,Values=$VPC_ID"
#       🇺🇦 Фільтр: повертати тільки NACL що належать нашій VPC
#       🇬🇧 Filter: return only NACLs belonging to our VPC
#
#   --query 'NetworkAcls[0].NetworkAclId'
#       🇺🇦 Перший результат (у нас один NACL) — беремо його ID
#       🇬🇧 First result (we have one NACL) — extract its ID

NACL_ID=$(aws ec2 describe-network-acls \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'NetworkAcls[0].NetworkAclId' \
  --output text)

echo "✅ NACL ID: $NACL_ID"
```

```bash
# aws ec2 create-network-acl-entry  (загальна структура / general structure)
#   --network-acl-id $NACL_ID   → NACL який редагуємо / NACL to edit
#   --ingress / --egress         → напрямок: вхідний / вихідний | direction: inbound / outbound
#   --rule-number NNN            → номер правила (1–32766); менший = вищий пріоритет
#                                  rule number (1–32766); lower = evaluated first
#   --protocol tcp/icmp/-1       → tcp=6, udp=17, icmp=1, -1=всі / all
#   --port-range From=X,To=Y     → діапазон портів / port range
#   --cidr-block 0.0.0.0/0       → до/від якої IP (0.0.0.0/0 = будь-якої) / any IP
#   --rule-action allow/deny     → дозволити або заборонити / permit or deny

# Правило 100 — вхідний SSH / Rule 100 — inbound SSH
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID --ingress --rule-number 100 \
  --protocol tcp --port-range From=22,To=22 \
  --cidr-block 0.0.0.0/0 --rule-action allow
echo "✅ Rule 100: SSH inbound — allow"

# Правило 110 — вхідний HTTP / Rule 110 — inbound HTTP
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID --ingress --rule-number 110 \
  --protocol tcp --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 --rule-action allow
echo "✅ Rule 110: HTTP inbound — allow"

# Правило 120 — вхідний ICMP (ping)
# --icmp-type-code Code=-1,Type=-1
#     🇺🇦 -1 означає "всі типи та коди ICMP" (ping = type 8, але дозволимо всі)
#     🇬🇧 -1 means "all ICMP types and codes" (ping = type 8, but we allow all)
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID --ingress --rule-number 120 \
  --protocol icmp --icmp-type-code Code=-1,Type=-1 \
  --cidr-block 0.0.0.0/0 --rule-action allow
echo "✅ Rule 120: ICMP (ping) inbound — allow"

# Правило 130 — ephemeral ports (відповіді TCP-серверів) / TCP server responses
# 🇺🇦 ВАЖЛИВО: NACL stateless! Коли ваш браузер з'єднується з EC2,
#     відповідь повертається через порт 1024–65535 (обраний ОС клієнта).
#     Без цього правила відповіді будуть заблоковані.
# 🇬🇧 IMPORTANT: NACL is stateless! When your browser connects to EC2,
#     responses come back on port 1024–65535 (chosen by the client OS).
#     Without this rule, all response packets would be blocked.
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID --ingress --rule-number 130 \
  --protocol tcp --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 --rule-action allow
echo "✅ Rule 130: Ephemeral ports inbound — allow"

# Правило 100 — весь вихідний трафік / Rule 100 — all outbound traffic
# --protocol -1  →  🇺🇦 -1 = всі протоколи (TCP, UDP, ICMP тощо)
#                   🇬🇧 -1 = all protocols (TCP, UDP, ICMP, etc.)
aws ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID --egress --rule-number 100 \
  --protocol -1 --cidr-block 0.0.0.0/0 --rule-action allow
echo "✅ Rule 100: All outbound — allow"
```

---

## 🛡️ Крок 6 — Security Group / Step 6 — Security Group

**🇺🇦** Security Group — другий рівень захисту на рівні **інстансу**. Є **stateful**: якщо дозволено вхідний трафік — відповідний вихідний дозволяється автоматично. Підтримує тільки правила "дозволити".

**🇬🇧** Security Group is the second defense layer at the **instance** level. It is **stateful**: permitting inbound traffic automatically allows the corresponding outbound response. Supports "allow" rules only.

```bash
# aws ec2 create-security-group
#   --group-name academy-sg
#       🇺🇦 Ім'я SG — унікальне в межах VPC
#       🇬🇧 Name — must be unique within the VPC
#
#   --description "..."
#       🇺🇦 Текстовий опис (обов'язкове поле!)
#       🇬🇧 Text description (required field!)
#
#   --vpc-id $VPC_ID
#       🇺🇦 VPC до якої належить ця Security Group
#       🇬🇧 The VPC this Security Group is associated with
#
#   --query 'GroupId'
#       🇺🇦 Витягуємо тільки ID з відповіді
#       🇬🇧 Extract only the GroupId from the response

SG_ID=$(aws ec2 create-security-group \
  --group-name academy-sg \
  --description "Security Group for Academy Lab" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=academy-sg}]' \
  --query 'GroupId' \
  --output text)

echo "✅ Security Group створено / created: $SG_ID"
```

```bash
# aws ec2 authorize-security-group-ingress
#   --group-id $SG_ID   → яку SG змінюємо / which SG to update
#   --protocol tcp      → протокол / protocol
#   --port 22           → порт / port number
#   --cidr 0.0.0.0/0   → з будь-якої адреси / from any source IP

# SSH — порт 22 / port 22
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0

# HTTP — порт 80 / port 80
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0

# ICMP (ping)
# --port -1
#     🇺🇦 Для ICMP -1 означає "всі типи ICMP" (ping, traceroute тощо)
#     🇬🇧 For ICMP, -1 means "all ICMP types" (ping, traceroute, etc.)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID --protocol icmp --port -1 --cidr 0.0.0.0/0

echo "✅ SG правила додано / rules added: SSH (22), HTTP (80), ICMP"
```

---

## 💻 Крок 7 — Запуск EC2-інстансів / Step 7 — Launch EC2 Instances

**🇺🇦** EC2 (Elastic Compute Cloud) — сервіс віртуальних машин AWS. `t2.micro` входить у Free Tier. `user-data` — скрипт що виконується при першому завантаженні інстансу.

**🇬🇧** EC2 (Elastic Compute Cloud) is the AWS VM service. `t2.micro` is Free Tier eligible. `user-data` is a bootstrap script executed once on the instance's first boot.

```bash
# Знаходимо найновіший AMI Amazon Linux 2023
# Find the latest Amazon Linux 2023 AMI

# aws ec2 describe-images
#   --owners amazon
#       🇺🇦 Тільки офіційні образи від Amazon (не сторонні)
#       🇬🇧 Only official Amazon-published images (not third-party)
#
#   --filters "Name=name,Values=al2023-ami-2023*-x86_64"
#       🇺🇦 Фільтр по імені: al2023 + будь-яка версія + архітектура x86_64
#           Зірочка (*) — wildcard як у bash
#       🇬🇧 Filter by name: al2023 + any version + x86_64 architecture
#           Asterisk (*) is a wildcard, same as in bash
#
#   --filters "Name=state,Values=available"
#       🇺🇦 Тільки доступні образи (не deprecated, не pending)
#       🇬🇧 Only available images (not deprecated or pending)
#
#   --query 'sort_by(Images, &CreationDate)[-1].ImageId'
#       🇺🇦 Сортуємо всі результати по даті створення,
#           [-1] бере останній елемент (найновіший), дістаємо його ImageId
#       🇬🇧 Sort all results by creation date,
#           [-1] takes the last element (newest), extract its ImageId

AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters \
    "Name=name,Values=al2023-ami-2023*-x86_64" \
    "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

echo "✅ AMI знайдено / AMI found: $AMI_ID"
```

```bash
# aws ec2 run-instances
#   --image-id $AMI_ID
#       🇺🇦 Який образ ОС використати для інстансу
#       🇬🇧 Which OS image to use for this instance
#
#   --instance-type t2.micro
#       🇺🇦 Розмір VM: t2.micro = 1 vCPU + 1 GB RAM, входить у Free Tier
#       🇬🇧 VM size: t2.micro = 1 vCPU + 1 GB RAM, Free Tier eligible
#
#   --subnet-id $SUBNET_A_ID
#       🇺🇦 В якій підмережі запустити (визначає AZ та IP-діапазон)
#       🇬🇧 Which subnet to launch in (determines AZ and IP range)
#
#   --security-group-ids $SG_ID
#       🇺🇦 Яку Security Group застосувати до цього інстансу
#       🇬🇧 Which Security Group to attach to this instance
#
#   --user-data '#!/bin/bash ...'
#       🇺🇦 Shell-скрипт що виконується при першому завантаженні.
#           Тут: встановлюємо Apache та кладемо тестову сторінку
#       🇬🇧 Shell script executed on first boot.
#           Here: install Apache and create a test webpage
#
#   --query 'Instances[0].InstanceId'
#       🇺🇦 З відповіді (масив Instances) беремо перший елемент, дістаємо InstanceId
#       🇬🇧 From the Instances array take the first element, extract InstanceId

INSTANCE_A_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --subnet-id $SUBNET_A_ID \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=WebServer}]' \
  --user-data '#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>WebServer — Subnet A ($(hostname -I))</h1>" > /var/www/html/index.html' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "✅ WebServer запущено / launched (Subnet-A): $INSTANCE_A_ID"
```

```bash
# AppServer — аналогічно, але у Subnet-B / Same command but for Subnet-B

INSTANCE_B_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --subnet-id $SUBNET_B_ID \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=AppServer}]' \
  --user-data '#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>AppServer — Subnet B ($(hostname -I))</h1>" > /var/www/html/index.html' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "✅ AppServer запущено / launched (Subnet-B): $INSTANCE_B_ID"
```

```bash
# aws ec2 wait instance-running
#   🇺🇦 Блокуюча команда: опитує AWS кожні 15 секунд,
#       повертає управління тільки коли всі інстанси у стані "running"
#   🇬🇧 Blocking command: polls AWS every 15 seconds,
#       returns only when all listed instances reach "running" state
#
#   --instance-ids $INSTANCE_A_ID $INSTANCE_B_ID
#       🇺🇦 Перелік інстансів через пробіл (можна вказати кілька)
#       🇬🇧 Space-separated list of instance IDs (multiple supported)

echo "⏳ Очікуємо запуску / Waiting for instances to start..."
aws ec2 wait instance-running \
  --instance-ids $INSTANCE_A_ID $INSTANCE_B_ID

echo "✅ Обидва інстанси запущені / Both instances running!"
```

---

## 🌍 Крок 8 — Elastic IP / Step 8 — Elastic IP: Allocate & Associate

**🇺🇦** Elastic IP (EIP) — статична публічна адреса. Звичайний публічний IP змінюється при перезапуску інстансу. EIP залишається незмінним і належить вашому акаунту доки не звільнено вручну.

**🇬🇧** Elastic IP (EIP) is a static public address. A regular public IP changes when the instance restarts. An EIP persists and belongs to your account until you explicitly release it.

```bash
# Отримуємо ENI (мережевий інтерфейс) кожного інстансу
# Get the ENI (network interface) of each instance

# ENI (Elastic Network Interface) — це віртуальна мережева карта.
# Elastic IP прив'язується саме до ENI, не безпосередньо до інстансу.
# Це дозволяє відв'язати ENI (з EIP) від одного інстансу та прикріпити до іншого.
#
# ENI (Elastic Network Interface) is the virtual network card.
# An Elastic IP binds to the ENI, not the instance directly.
# This allows you to detach an ENI (with EIP) from one instance and attach to another.

ENI_A=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_A_ID \
  --query 'Reservations[0].Instances[0].NetworkInterfaces[0].NetworkInterfaceId' \
  --output text)

ENI_B=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_B_ID \
  --query 'Reservations[0].Instances[0].NetworkInterfaces[0].NetworkInterfaceId' \
  --output text)

echo "ENI WebServer: $ENI_A"
echo "ENI AppServer: $ENI_B"
```

```bash
# aws ec2 allocate-address
#   --domain vpc
#       🇺🇦 Вказуємо що цей EIP для VPC-середовища.
#           Застаріла альтернатива — EC2-Classic (більше не підтримується)
#       🇬🇧 Specify VPC domain.
#           The legacy alternative EC2-Classic is no longer supported
#
#   --query 'AllocationId'
#       🇺🇦 AllocationId — унікальний ID виділення цього EIP у вашому акаунті
#           Використовуємо його (не IP) у подальших командах
#       🇬🇧 AllocationId — unique ID for this EIP allocation in your account
#           Use this (not the IP) in subsequent commands

EIP_ALLOC_ID=$(aws ec2 allocate-address \
  --domain vpc \
  --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=academy-eip}]' \
  --query 'AllocationId' \
  --output text)

EIP_ADDRESS=$(aws ec2 describe-addresses \
  --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].PublicIp' \
  --output text)

echo "✅ Elastic IP виділено / allocated: $EIP_ADDRESS  (ID: $EIP_ALLOC_ID)"
```

### 8.1 — Прив'язка до WebServer / Associate → WebServer

```bash
# aws ec2 associate-address
#   --allocation-id $EIP_ALLOC_ID
#       🇺🇦 ID виділеного EIP (який прив'язуємо)
#       🇬🇧 The allocation ID of the EIP to associate
#
#   --network-interface-id $ENI_A
#       🇺🇦 ENI до якого прив'язуємо (мережева карта WebServer)
#       🇬🇧 The ENI to bind to (WebServer's network interface)

aws ec2 associate-address \
  --allocation-id $EIP_ALLOC_ID \
  --network-interface-id $ENI_A

echo "✅ $EIP_ADDRESS → WebServer (Subnet-A)"
echo "🌐 Відкрийте / Open in browser: http://$EIP_ADDRESS"
```

> ⏳ Зачекайте ~2–3 хв поки `user-data` встановить Apache. / Wait ~2–3 min for `user-data` to install Apache.

### 8.2 — Перевірка прив'язки / Verify association

```bash
aws ec2 describe-addresses \
  --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].{IP:PublicIp,Instance:InstanceId,ENI:NetworkInterfaceId}' \
  --output table
```

---

## 🔄 Крок 9 — Переміщення EIP / Step 9 — Move EIP to AppServer

**🇺🇦** Переміщуємо EIP з WebServer на AppServer. IP-адреса **не змінюється** — змінюється лише куди вона вказує. Це демонструє цінність Elastic IP: швидке перенаправлення трафіку без зміни DNS.

**🇬🇧** Move the EIP from WebServer to AppServer. The IP address **does not change** — only where it points does. This demonstrates the value of Elastic IP: instant traffic redirection without touching DNS records.

```bash
# Крок 1: отримуємо AssociationId поточної прив'язки
# Step 1: get the AssociationId of the current binding
#
# 🇺🇦 AssociationId ≠ AllocationId!
#     AllocationId = ID самого EIP у вашому акаунті (незмінний)
#     AssociationId = ID конкретної прив'язки EIP до ENI (змінюється при кожному associate)
# 🇬🇧 AssociationId ≠ AllocationId!
#     AllocationId = ID of the EIP itself in your account (permanent)
#     AssociationId = ID of the current EIP-to-ENI binding (changes each time you associate)

ASSOC_ID=$(aws ec2 describe-addresses \
  --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].AssociationId' \
  --output text)

echo "Поточна прив'язка / Current association: $ASSOC_ID"
```

```bash
# Крок 2: відв'язуємо EIP від WebServer
# Step 2: detach EIP from WebServer
#
# aws ec2 disassociate-address
#   --association-id $ASSOC_ID
#       🇺🇦 Передаємо AssociationId — НЕ AllocationId!
#           Відв'язуємо конкретну прив'язку, сам EIP залишається у нас
#       🇬🇧 Pass the AssociationId — NOT the AllocationId!
#           We detach the binding; the EIP itself stays in our account

aws ec2 disassociate-address \
  --association-id $ASSOC_ID

echo "✅ EIP відв'язано від WebServer / EIP detached from WebServer"
```

```bash
# Крок 3: прив'язуємо до AppServer
# Step 3: attach to AppServer

aws ec2 associate-address \
  --allocation-id $EIP_ALLOC_ID \
  --network-interface-id $ENI_B

echo "✅ $EIP_ADDRESS → AppServer (Subnet-B)"
echo "🌐 Той самий IP, інший сервер / Same IP, different server: http://$EIP_ADDRESS"
```

> ⚡ **Результат / Result:** Адреса `$EIP_ADDRESS` залишилась тією ж, але браузер тепер показує **AppServer**! / Address `$EIP_ADDRESS` is unchanged, but the browser now shows **AppServer**!

---

## 📊 Крок 10 — Фінальний огляд / Step 10 — Final Summary

```bash
echo "════════════════════════════════════════════════════"
echo "    ПІДСУМОК ІНФРАСТРУКТУРИ / INFRASTRUCTURE SUMMARY"
echo "════════════════════════════════════════════════════"

echo -e "\n🏢 VPC:"
aws ec2 describe-vpcs --vpc-ids $VPC_ID \
  --query 'Vpcs[0].{ID:VpcId,CIDR:CidrBlock,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table

echo -e "\n📦 Subnets:"
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[*].{ID:SubnetId,CIDR:CidrBlock,AZ:AvailabilityZone,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table

echo -e "\n💻 Instances:"
aws ec2 describe-instances \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].{ID:InstanceId,State:State.Name,PrivIP:PrivateIpAddress,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table

echo -e "\n🌍 Elastic IP:"
aws ec2 describe-addresses --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].{IP:PublicIp,Instance:InstanceId,AllocID:AllocationId}' \
  --output table
```

---

## 💾 Збережіть ваші змінні / Save Your Variable Values

```bash
# Виконайте та збережіть результат / Run and save the output
cat << EOF
=== ЗБЕРЕЖІТЬ / SAVE ===
VPC_ID=$VPC_ID
SUBNET_A_ID=$SUBNET_A_ID
SUBNET_B_ID=$SUBNET_B_ID
IGW_ID=$IGW_ID
RT_ID=$RT_ID
SG_ID=$SG_ID
NACL_ID=$NACL_ID
INSTANCE_A_ID=$INSTANCE_A_ID
INSTANCE_B_ID=$INSTANCE_B_ID
EIP_ALLOC_ID=$EIP_ALLOC_ID
EIP_ADDRESS=$EIP_ADDRESS
ENI_A=$ENI_A
ENI_B=$ENI_B
EOF
```

---

## 🧹 Крок 11 — Очищення / Step 11 — Cleanup

> ⚠️ Виконайте обов'язково після заняття! AWS Academy має ліміти ресурсів.
> ⚠️ Run after the lab! AWS Academy has resource quotas.

```bash
# Порядок важливий: видаляємо у зворотному порядку залежностей
# Order matters: delete in reverse dependency order

ASSOC_ID=$(aws ec2 describe-addresses --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].AssociationId' --output text 2>/dev/null)
[ -n "$ASSOC_ID" ] && [ "$ASSOC_ID" != "None" ] && \
  aws ec2 disassociate-address --association-id $ASSOC_ID
aws ec2 release-address --allocation-id $EIP_ALLOC_ID && echo "✅ EIP released"

aws ec2 terminate-instances --instance-ids $INSTANCE_A_ID $INSTANCE_B_ID
echo "⏳ Waiting for termination..."
aws ec2 wait instance-terminated --instance-ids $INSTANCE_A_ID $INSTANCE_B_ID
echo "✅ Instances terminated"

aws ec2 delete-security-group --group-id $SG_ID && echo "✅ SG deleted"
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID && echo "✅ IGW deleted"
aws ec2 delete-subnet --subnet-id $SUBNET_A_ID
aws ec2 delete-subnet --subnet-id $SUBNET_B_ID && echo "✅ Subnets deleted"
aws ec2 delete-route-table --route-table-id $RT_ID && echo "✅ Route Table deleted"
aws ec2 delete-vpc --vpc-id $VPC_ID && echo "✅ VPC deleted"

echo ""
echo "🎉 Cleanup complete!"
```

---

## 📚 Ключові концепції / Key Concepts

| Сервіс | 🇺🇦 Опис | 🇬🇧 Description | Аналогія / Analogy |
|---|---|---|---|
| **VPC** | Ізольована мережа | Isolated cloud network | Приватна кімната / Private room |
| **Subnet** | Підмережа у VPC | Sub-network inside VPC | Кімнати всередині / Rooms inside |
| **IGW** | Шлюз до інтернету | Gateway to internet | Вхідні двері / Front door |
| **Route Table** | Таблиця маршрутів | Traffic routing rules | Вказівники / Road signs |
| **Security Group** | Firewall інстансу | Instance-level firewall | Охоронець в дверях / Door guard |
| **Network ACL** | Firewall підмережі | Subnet-level firewall | Охоронець поверху / Floor guard |
| **Elastic IP** | Статична публічна IP | Static public IP | Постійна адреса / Fixed address |
| **EC2** | Віртуальна машина | Virtual machine | Сервер у хмарі / Cloud server |
| **ENI** | Мережева карта | Virtual network card | Мережевий роз'єм / Network port |
| **AMI** | Образ системи | Machine image template | Шаблон ОС / OS template |

---

## 🎯 Самоперевірка / Self-Assessment

```bash
curl -O https://raw.githubusercontent.com/rossogamata/mar251-2/main/self_check/check.sh
chmod +x check.sh && ./check.sh
```

---

*Підготовлено для AWS Academy Learner Lab | Методології автоматизованого розгортання ІТ інфраструктури — 5 курс*
*Prepared for AWS Academy Learner Lab | Cloud Technologies — 5th Year* 🇺🇦
