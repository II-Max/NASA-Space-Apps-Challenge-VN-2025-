# weather_nasa_3cities.py
import requests
from datetime import datetime
import json
import pandas as pd
import os

class NASAWeather:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_nasa_gmao_forecast(self, latitude, longitude):
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
        """DATA PROCESSING - Trả về dữ liệu dự báo chi tiết"""
        try:
            current = data['current']
            hourly = data['hourly']
            daily = data['daily']

            hourly_forecast = []
            # Lấy toàn bộ 24 khung giờ dự báo
            for i in range(len(hourly['time'])):
                hourly_forecast.append({
                    'time': hourly['time'][i],
                    'temperature_2m': hourly['temperature_2m'][i],
                    'precipitation': hourly['precipitation'][i],
                    'wind_speed_10m': hourly['wind_speed_10m'][i]
                })

            return {
                'thanh_pho': '',
                'nguon': 'NASA GMAO Model via Open-Meteo',
                'thoi_gian': current['time'],
                'vi_do': lat,
                'kinh_do': lon,
                'nhiet_do_hien_tai': current['temperature_2m'],
                'do_am': current['relative_humidity_2m'],
                'luong_mua_hien_tai': current['precipitation'],
                'gio_toc_do_hien_tai': current['wind_speed_10m'],
                'ma_thoi_tiet': current['weather_code'],
                'nhiet_do_cao_nhat_ngay': daily['temperature_2m_max'][0],
                'nhiet_do_thap_nhat_ngay': daily['temperature_2m_min'][0],
                'tong_luong_mua_ngay': daily['precipitation_sum'][0],
                'du_bao_ca_ngay': hourly_forecast, # Lưu trữ toàn bộ dữ liệu dự báo 24h
                'la_du_bao': True,
                'thoi_gian_cap_nhat': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except KeyError as e:
            print(f"❌ Lỗi xử lý dữ liệu dự báo: {e}")
            return None
    
    def get_weather_data(self, city_name, latitude, longitude):
        print(f"🌍 Đang lấy dữ liệu thời tiết cho {city_name}...")
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
        """Lưu dữ liệu vào file Excel, bao gồm 24h dự báo"""
        if not weather_data:
            return False
        try:
            # Chuẩn bị dữ liệu cho DataFrame
            excel_data = []
            base_info = {
                'Thành_phố': city_name,
                'Nguồn_dữ_liệu': weather_data['nguon'],
                'Thời_gian_cập_nhật': weather_data['thoi_gian_cap_nhat'],
                'Vĩ_độ': weather_data['vi_do'],
                'Kinh_độ': weather_data['kinh_do'],
                'Nhiệt_độ_hiện_tại (C)': weather_data['nhiet_do_hien_tai'],
                'Độ_ẩm (%)': weather_data['do_am'],
                'Lượng_mưa_hiện_tại (mm)': weather_data['luong_mua_hien_tai'],
                'Gió_tốc_độ_hiện_tại (m/s)': weather_data['gio_toc_do_hien_tai'],
                'Mã_thoi_tiet': weather_data['ma_thoi_tiet'],
                'Nhiệt_độ_cao_nhất_ngày (C)': weather_data['nhiet_do_cao_nhat_ngay'],
                'Nhiệt_độ_thấp_nhất_ngày (C)': weather_data['nhiet_do_thap_nhat_ngay'],
                'Tổng_lượng_mưa_ngày (mm)': weather_data['tong_luong_mua_ngay'],
                'Là_dự_báo': 'Có' if weather_data['la_du_bao'] else 'Không'
            }

            # Thêm dữ liệu dự báo theo 24 giờ
            for forecast in weather_data['du_bao_ca_ngay']:
                row = base_info.copy()
                row['Dự_báo_giờ'] = forecast['time']
                row['Nhiệt_độ_giờ (C)'] = forecast['temperature_2m']
                row['Lượng_mưa_giờ (mm)'] = forecast['precipitation']
                row['Gió_tốc_độ_giờ (m/s)'] = forecast['wind_speed_10m']
                excel_data.append(row)

            # Tạo DataFrame và lưu vào Excel
            df = pd.DataFrame(excel_data)
            os.makedirs("datatypexlsx", exist_ok=True)
            filename = os.path.join("datatypexlsx", f"{city_name}_24h.xlsx")
            df.to_excel(filename, index=False, engine='openpyxl')
            
            print(f"💾 Đã lưu file: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu file Excel: {e}")
            return False

def display_weather_info(weather_data, city_name):
    """Hiển thị thông tin thời tiết đã tối ưu"""
    if not weather_data:
        print(f"❌ Không có dữ liệu cho {city_name}")
        return
    
    print(f"\n🌤️ THÔNG TIN THỜI TIẾT - {city_name.upper()}")
    print("="*50)
    print("➡️ THỜI TIẾT HIỆN TẠI:")
    print(f"📊 Nguồn: {weather_data['nguon']}")
    print(f"📅 Thời gian: {weather_data['thoi_gian']}")
    print(f"🌡️ Nhiệt độ: {weather_data['nhiet_do_hien_tai']}°C")
    print(f"💧 Độ ẩm: {weather_data['do_am']}%")
    print(f"💨 Gió: {weather_data['gio_toc_do_hien_tai']} m/s")
    print(f"📈 Tổng mưa ngày: {weather_data['tong_luong_mua_ngay']}mm")
    print("---")
    
    print("🔮 DỰ BÁO 24H TIẾP THEO:")
    for forecast in weather_data['du_bao_ca_ngay']:
        time_str = datetime.fromisoformat(forecast['time']).strftime("%H:%M")
        print(f"   - Giờ {time_str}: Nhiệt độ: {forecast['temperature_2m']}°C, Mưa: {forecast['precipitation']}mm, Gió: {forecast['wind_speed_10m']} m/s")
    
    print("="*50)

def main():
    """Hàm chính"""
    print("🚀 ỨNG DỤNG LẤY DỮ LIỆU THỜI TIẾT TỪ NASA")
    print("📡 RUNNING...\n")
    
    cities = {
        "1": {"name": "Ninh Bình", "coords": (20.2506, 105.9745)},
        "2": {"name": "Hồ Chí Minh", "coords": (10.8231, 106.6297)},
        "3": {"name": "Hà Nội", "coords": (21.0278, 105.8342)}
    }
    
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
                    selected_cities = list(cities.values())
                else:
                    selected_cities = [cities[choice]]
                
                for city_info in selected_cities:
                    city_name = city_info["name"]
                    lat, lon = city_info["coords"]
                    
                    weather_data = nasa_client.get_weather_data(city_name, lat, lon)
                    
                    if weather_data:
                        display_weather_info(weather_data, city_name)
                        nasa_client.save_to_json(weather_data, city_name)
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
