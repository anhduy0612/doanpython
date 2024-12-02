import time
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException

# Định nghĩa các router.
R1 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.154.10",
    "username": "admin",
    "password": "123",
}
R2 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.154.20",
    "username": "admin",
    "password": "123",
}
R3 = {
    "device_type": "mikrotik_routeros",
    "ip": "192.168.154.30",
    "username": "admin",
    "password": "123",
}
list_router = [R1, R2, R3]

# Hàm xử lý kết nối đến router với cơ chế thử lại
def connect_to_router(router, retries=2, delay=2):
    """
    Thử kết nối đến router, nếu không thành công sẽ thử lại sau một khoảng thời gian.
    """
    attempt = 0
    while attempt < retries:
        try:
            # Cố gắng kết nối đến router
            return ConnectHandler(**router)
        except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
            attempt += 1
            print(f"Không thể kết nối với router {router['ip']}. Lý do: {e}. Thử lại lần {attempt}/{retries}.")
            if attempt < retries:
                time.sleep(delay)  # Chờ 2 giây trước khi thử lại
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}. Không thể kết nối với router {router['ip']}.")
            break
    print(f"Không thể kết nối với router {router['ip']} sau {retries} lần thử.")
    return None

# Hiển thị menu cho người dùng
def menu():
    print("\n1. Show tất cả các router")
    print("2. Show địa chỉ IP của từng router")
    print("3. Kiểm tra kết nối mạng với các router")
    print("4. Thêm/Xóa địa chỉ IP vào router")
    print("5. Thêm/Xóa địa chỉ DHCP vào router")
    print("6. Thoát chương trình")
    try:
        return int(input("Chọn một tùy chọn (1-6): "))
    except ValueError:
        print("Lựa chọn không hợp lệ. Vui lòng chọn từ 1 đến 6.")
        return None

# Hiển thị thông tin tất cả các router
def show_all_routers():
    for router in list_router:
        net_connect = connect_to_router(router)
        if net_connect:
            name = net_connect.send_command("/system identity print")
            print(f"Router: {router['ip']}")
            print(f"Tên router: {name}")
            print("-------------")

# Hiển thị địa chỉ IP của từng router
def show_ip_addresses():
    for router in list_router:
        net_connect = connect_to_router(router)
        if net_connect:
            output = net_connect.send_command("/ip address print")
            print(f"Địa chỉ IP của router {router['ip']}:")
            print(output)
            print("-------------")

# Kiểm tra kết nối mạng với các router
def check_network_connection():
    for router in list_router:
        net_connect = connect_to_router(router)
        if net_connect:
            print(f"Kết nối thành công với router {router['ip']}")
        else:
            print(f"Kết nối thất bại với router {router['ip']}.")

# Thêm hoặc xóa địa chỉ IP trên router
def modify_ip_address():
    print("Danh sách các router:")
    for i, router in enumerate(list_router):
        print(f"{i + 1}. Router {router['ip']}")
    
    try:
        choice = int(input("Chọn router bạn muốn thay đổi địa chỉ IP (1-3): ")) - 1
        if choice not in range(len(list_router)):
            print("Chọn không hợp lệ. Vui lòng thử lại.")
            return
    except ValueError:
        print("Lựa chọn không hợp lệ.")
        return

    net_connect = connect_to_router(list_router[choice])
    if not net_connect:
        return

    action = input("Bạn muốn thêm hay xóa địa chỉ IP (add/remove): ").strip().lower()
    if action == "add":
        ip_address = input("Nhập địa chỉ IP muốn thêm (VD: 192.168.109.10/24): ")
        interface = input("Nhập tên interface (VD: ether1): ")
        command = f"/ip address add address={ip_address} interface={interface}"
        net_connect.send_command(command)
        print(f"Đã thêm địa chỉ IP {ip_address} vào router {list_router[choice]['ip']}")
    elif action == "remove":
        print("Danh sách các địa chỉ IP hiện có trên router:")
        ip_addresses = net_connect.send_command("/ip address print")
        print(ip_addresses)
        try:
            value1 = int(input("Nhập số dòng muốn xóa:"))
            command = f"/ip address remove numbers={value1}"
            net_connect.send_command(command)
            print(f"Đã xóa địa chỉ IP khỏi router {list_router[choice]['ip']}")
        except ValueError:
            print("Lựa chọn không hợp lệ, vui lòng nhập một số hợp lệ.")
    else:
        print("Lệnh không hợp lệ, vui lòng chọn 'add' hoặc 'remove'.")

# Cấu hình DHCP trên router
def add_dhcp():
    print("Danh sách các router:")
    for i, router in enumerate(list_router):
        print(f"{i + 1}. Router {router['ip']}")
    
    try:
        choice = int(input("Chọn router bạn muốn cấu hình DHCP (1-3): ")) - 1
        if choice not in range(len(list_router)):
            print("Chọn không hợp lệ. Vui lòng thử lại.")
            return
    except ValueError:
        print("Lựa chọn không hợp lệ.")
        return

    net_connect = connect_to_router(list_router[choice])
    if not net_connect:
        return

    action = input("Bạn muốn thêm hay xóa DHCP (add/remove): ").strip().lower()
    if action == "add":
        address = input("Nhập địa chỉ mạng (VD: 192.168.109.0/24): ")
        interface = input("Nhập tên interface (VD: ether1): ")
        gateway = input("Nhập địa chỉ Gateway (VD: 192.168.109.1): ")
        dns = input("Nhập địa chỉ DNS (VD: 8.8.8.8, 8.8.4.4): ")
        range_start = input("Nhập địa chỉ IP đầu (VD: 192.168.109.100): ")
        range_end = input("Nhập địa chỉ IP cuối (VD: 192.168.109.200): ")

        commands = [
            f"/ip address add address={address} interface={interface}",
            f"/ip pool add name=dhcp_pool ranges={range_start}-{range_end}",
            f"/ip dhcp-server add name=dhcp1 interface={interface} address-pool=dhcp_pool disabled=no",
            f"/ip dhcp-server network add address={address} gateway={gateway} dns-server={dns}",
        ]
        for command in commands:
            net_connect.send_command(command)
        print(f"Đã thêm DHCP vào router {list_router[choice]['ip']}")
    elif action == "remove":
        print("Danh sách các địa chỉ IP hiện có trên router:")
        ip_addresses = net_connect.send_command("/ip address print")
        print(ip_addresses)
        value1 = input("Nhập số dòng muốn xóa:")
        value1 = int(value1)
        command = f"/ip address remove numbers={value1}"
        net_connect.send_command(command)
        print(f"Đã xóa ip cua dhcp khỏi router {list_router[choice]['ip']}")
    else:
        print("Lệnh không hợp lệ, vui lòng chọn 'add' hoặc 'remove'.")

# Chương trình chính
while True:
    try:
        option = menu()
        if option == 1:
            show_all_routers()
        elif option == 2:
            show_ip_addresses()
        elif option == 3:
            check_network_connection()
        elif option == 4:
            modify_ip_address()
        elif option == 5:
            add_dhcp()
        elif option == 6:
            break
        elif option is None:  # Nếu input không hợp lệ
            continue  # Tiếp tục vòng lặp và yêu cầu người dùng nhập lại
        else:
            print("Tùy chọn không hợp lệ, hãy thử lại.")

        # Yêu cầu người dùng xác nhận có muốn tiếp tục hay không
        while True:  # Lặp lại yêu cầu cho đến khi nhập đúng
            cont = input("Bạn có muốn tiếp tục không? (y/n): ").strip().lower()
            if cont == 'y':
                break  # Tiếp tục vòng lặp chính nếu nhập 'y'
            elif cont == 'n':
                print("Chương trình kết thúc.")
                break  # Thoát vòng lặp chính nếu nhập 'n'
            else:
                print("Lựa chọn không hợp lệ. Vui lòng nhập 'y' hoặc 'n'.")

        if cont == 'n':  # Thoát vòng lặp chính khi người dùng chọn 'n'
            break
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}. Chương trình sẽ tiếp tục.")
