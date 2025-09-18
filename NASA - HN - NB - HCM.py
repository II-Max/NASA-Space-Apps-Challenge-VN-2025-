# weather_nasa_3cities.py
import requests
from datetime import datetime, timedelta
import json
import pandas as pd
import os
class NASAWeather:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_nasa_gmao_forecast (self, latitude, longitude):
        """Lấy dữ liệu dự báo sử dụng model NASA GMAO thông qua Open-Meteo"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code',
            'hourly': 'temperature_2m,precipitation,wind_speed_10m',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
            'timezone': 'auto',
            'forecast_days': 1
        }
        try:
            print(f"📡 CONNECTING NASA GMAO...")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_forecast_data(data, latitude, longitude)
            else:
                print(f"❌ Lỗi {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return None
    def _process_forecast_data(self, data, lat, lon):
        """DATA PROCESSING"""
        try:
            current = data['current']
            hourly = data['hourly']
            daily = data['daily']
            # Lấy dữ liệu cho giờ hiện tại
            current_time = datetime.now().strftime("%Y-%m-%dT%H:00")
            if current_time in hourly['time']:
                time_index = hourly['time'].index(current_time)
                hourly_temp = hourly['temperature_2m'][time_index]
                hourly_precip = hourly['precipitation'][time_index]
                hourly_wind = hourly['wind_speed_10m'][time_index]
            else:
                hourly_temp = current['temperature_2m']
                hourly_precip = current['precipitation']
                hourly_wind = current['wind_speed_10m']
            return {
                'thanh_pho': '',
                'nguon': 'NASA GMAO Model via Open-Meteo',
                'thoi_gian': current['time'],
                'vi_do': lat,
                'kinh_do': lon,
                'nhiet_do_hien_tai': current['temperature_2m'],
                'nhiet_do_gio': hourly_temp,
                'nhiet_do_cao_nhat': daily['temperature_2m_max'][0],
                'nhiet_do_thap_nhat': daily['temperature_2m_min'][0],
                'do_am': current['relative_humidity_2m'],
                'luong_mua_hien_tai': current['precipitation'],
                'luong_mua_gio': hourly_precip,
                'tong_luong_mua_ngay': daily['precipitation_sum'][0],
                'gio_toc_do': current['wind_speed_10m'],
                'gio_toc_do_gio': hourly_wind,
                'ma_thoi_tiet': current['weather_code'],
                'la_du_bao': True,
                'thoi_gian_cap_nhat': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except KeyError as e:
            print(f"❌ Lỗi xử lý dữ liệu dự báo: {e}")
            return None
    
    def get_weather_data(self, city_name, latitude, longitude):
        print(f"🌍 Đang lấy dữ liệu thời tiết cho {city_name}...")
        # Thử lấy dữ liệu dự báo trước
        weather_data = self.get_nasa_gmao_forecast(latitude, longitude)
        if weather_data:
            weather_data['thanh_pho'] = city_name
            print(f"✅ Đã lấy dữ liệu thành công cho {city_name}")
            return weather_data
        print(f"❌ Không thể lấy dữ liệu cho {city_name}")
        return None
    def save_to_json(self, weather_data, city_name):
        """Lưu dữ liệu vào file JSON"""
        if not weather_data:
            return False
        try:
            os.makedirs("datatypejs", exist_ok=True)
            filename = os.path.join("datatypejs", f"{city_name}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Đã lưu file: {filename}")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi lưu file JSON: {e}")
            return False
    
    def save_to_excel(self, weather_data, city_name):
        """Lưu dữ liệu vào file Excel"""
        if not weather_data:
            return False
        try:
            # Chuẩn bị dữ liệu cho Excel
            excel_data = [{
                'Thành_phố': city_name,
                'Nguồn_dữ_liệu': weather_data['nguon'],
                'Thời_gian': weather_data['thoi_gian'],
                'Vĩ_độ': weather_data['vi_do'],
                'Kinh_độ': weather_data['kinh_do'],
                'Nhiệt_độ_hiện_tại (°C)': weather_data['nhiet_do_hien_tai'],
                'Nhiệt_độ_giờ (°C)': weather_data['nhiet_do_gio'],
                'Nhiệt_độ_cao_nhất (°C)': weather_data['nhiet_do_cao_nhat'],
                'Nhiệt_độ_thấp_nhất (°C)': weather_data['nhiet_do_thap_nhat'],
                'Độ_ẩm (%)': weather_data['do_am'],
                'Lượng_mưa_hiện_tại (mm)': weather_data['luong_mua_hien_tai'],
                'Lượng_mưa_giờ (mm)': weather_data['luong_mua_gio'],
                'Tổng_lượng_mưa_ngày (mm)': weather_data['tong_luong_mua_ngay'],
                'Gió_tốc_độ (m/s)': weather_data['gio_toc_do'],
                'Gió_tốc_độ_giờ (m/s)': weather_data['gio_toc_do_gio'],
                'Mã_thời_tiet': weather_data['ma_thoi_tiet'],
                'Là_dự_báo': 'Có' if weather_data['la_du_bao'] else 'Không',
                'Thời_gian_cập_nhật': weather_data['thoi_gian_cap_nhat']
            }]
            
            # Tạo DataFrame và lưu vào Excel
            df = pd.DataFrame(excel_data)
            os.makedirs("datatypexlsx", exist_ok=True)
            filename = os.path.join("datatypexlsx", f"{city_name}.xlsx")
            df.to_excel(filename, index=False, engine='openpyxl')
            
            print(f"💾 Đã lưu file: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu file Excel: {e}")
            return False

def display_weather_info(weather_data, city_name):
    """Hiển thị thông tin thời tiết"""
    if not weather_data:
        print(f"❌ Không có dữ liệu cho {city_name}")
        return
    # In Dữ Liệu Ra Ngay
    print(f"\n🌤️  THÔNG TIN THỜI TIẾT - {city_name.upper()}")
    print("="*50)
    print(f"📍 Vị trí: {weather_data['vi_do']}°N, {weather_data['kinh_do']}°E")
    print(f"📅 Thời gian: {weather_data['thoi_gian']}")
    print(f"📊 Nguồn: {weather_data['nguon']}")
    print("="*50)
    print(f"🌡️  Nhiệt độ hiện tại: {weather_data['nhiet_do_hien_tai']}°C")
    print(f"🌡️  Nhiệt độ giờ: {weather_data['nhiet_do_gio']}°C")
    print(f"⬆️  Cao nhất: {weather_data['nhiet_do_cao_nhat']}°C")
    print(f"⬇️  Thấp nhất: {weather_data['nhiet_do_thap_nhat']}°C")
    print(f"💧 Độ ẩm: {weather_data['do_am']}%")
    print(f"🌧️  Mưa hiện tại: {weather_data['luong_mua_hien_tai']}mm")
    print(f"🌧️  Mưa giờ: {weather_data['luong_mua_gio']}mm")
    print(f"📈 Tổng mưa ngày: {weather_data['tong_luong_mua_ngay']}mm")
    print(f"💨 Gió: {weather_data['gio_toc_do']} m/s")
    print("="*50)
def main():
    """Hàm chính"""
    print("🚀 ỨNG DỤNG LẤY DỮ LIỆU THỜI TIẾT TỪ NASA")
    print("📡 RUNNING...\n")
    # Danh sách 3 thành phố
    cities = {
        "1": {"name": "Ninh Bình", "coords": (20.2506, 105.9745)},
        "2": {"name": "Hồ Chí Minh", "coords": (10.8231, 106.6297)},
        "3": {"name": "Hà Nội", "coords": (21.0278, 105.8342)}
    }
    # Tạo client NASA
    nasa_client = NASAWeather()
    while True:
        print("📍 CHỌN THÀNH PHỐ:")
        print("1. Ninh Bình")
        print("2. Hồ Chí Minh")
        print("3. Hà Nội")
        print("4. Tất cả 3 thành phố")
        print("0. Thoát")
        try:
            choice = input("\n👉 Nhập lựa chọn của bạn (0-4): ").strip()
            
            if choice == "0":
                print("👋 Tạm biệt!")
                break
            
            elif choice in ["1", "2", "3", "4"]:
                selected_cities = []
                
                if choice == "4":
                    # Lấy tất cả 3 thành phố
                    selected_cities = list(cities.values())
                    print("🌍 Đang lấy dữ liệu cho cả 3 thành phố...")
                else:
                    # Lấy 1 thành phố
                    city_info = cities[choice]
                    selected_cities = [city_info]
                    print(f"🌍 Đang lấy dữ liệu cho {city_info['name']}...")
                
                # Lấy dữ liệu cho các thành phố đã chọn
                for city_info in selected_cities:
                    city_name = city_info["name"]
                    lat, lon = city_info["coords"]
                    
                    # Lấy dữ liệu thời tiết
                    weather_data = nasa_client.get_weather_data(city_name, lat, lon)
                    
                    if weather_data:
                        # Hiển thị thông tin
                        display_weather_info(weather_data, city_name)
                        
                        # Lưu vào file JSON
                        nasa_client.save_to_json(weather_data, city_name)
                        
                        # Lưu vào file Excel
                        nasa_client.save_to_excel(weather_data, city_name)
                        
                        print(f"✅ Hoàn thành xử lý cho {city_name}\n")
                    else:
                        print(f"❌ Không thể lấy dữ liệu cho {city_name}\n")
                
                print("🎉 Đã xử lý xong tất cả thành phố được chọn!")
                
            else:
                print("❌ Lựa chọn không hợp lệ! Vui lòng chọn từ 0-4")
                
        except ValueError:
            print("❌ Vui lòng nhập số hợp lệ!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 GOODBYE")
