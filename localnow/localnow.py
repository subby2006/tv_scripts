import requests
from flask import Flask, redirect
from urllib.parse import urljoin

app = Flask(__name__)

channel_url = {
    'localnow.m3u8': 'https://data-store-trans-cdn.api.cms.amdvids.com/video/play/47A91849-985F-48FD-8517-CC5818930F90/1920/1080',
    'moviesplus.m3u8': 'https://data-store-trans-cdn.api.cms.amdvids.com/video/play/6D30170C-D7B3-46A2-8C1F-302D8399F44D/1920/1080',
    'nbc5news.m3u8': 'https://data-store-trans-cdn.api.cms.amdvids.com/video/play/44934351-EB30-4045-8421-FD35CE6E689F/1920/1080',
    'vevopop.m3u8': 'https://data-store-trans-cdn.api.cms.amdvids.com/video/play/3864C0AD-FFAA-46F7-8DBE-C7EC0298C5DD/1920/1080',
    'vevocountry.m3u8': 'https://data-store-trans-cdn.api.cms.amdvids.com/video/play/5157E7A2-7114-4F5C-8428-69044D464C00/1920/1080'
}

with open('token.txt', 'r') as file:
    token = file.read().strip()

headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "x-access-token": token.encode('utf-8').decode('latin-1'),
}

# Send the request
# response = requests.get(url, headers=headers)

# Print the response status and body
#print("Response Status Code:", response.status_code)

@app.route('/redirector/localnow/<path:channel>')
def get_stream(channel):
    if channel in channel_url:
        json_url = channel_url[channel]
        print(f"[DEBUG] Fetching JSON data from: {json_url} ") 
        
        response = requests.get(json_url, headers=headers)

        if response.headers.get('Content-Type') == 'application/json':
            json_data = response.json()
            # Extract the video_m3u8 URL
            if 'video_m3u8' in json_data:
                m3u8_url = json_data['video_m3u8']
                print("[DEBUG] video_m3u8 URL:", m3u8_url)

                # Fetch the M3U8 content
                m3u8_response = requests.get(m3u8_url)
                m3u8_content = m3u8_response.text

                # Find the first stream URL in the M3U8 content
                lines = m3u8_content.splitlines()
                if channel == "moviesplus.m3u8":
                    for line in lines:
                        if line.endswith('3.m3u8'):
                            relative_url = line.strip()
                            break
                elif channel == "nbc5news.m3u8":
                    for line in lines:
                        if line.endswith('2.m3u8'):
                            relative_url = line.strip()
                            break
                elif channel == "vevopop.m3u8" or channel == "vevocountry.m3u8":
                    for line in lines:
                        if line.endswith('4.m3u8'):
                            relative_url = line.strip()
                            break
                else:
                    for line in lines:
                        if line and not line.startswith('#'):
                            relative_url = line
                            break
                
                
                # Construct the absolute URL
                absolute_url = urljoin(m3u8_url, relative_url)
                print("[DEBUG] HQ stream absolute URL:", absolute_url)
                
                return redirect(absolute_url, code=302)
            else:
                print("[ERROR] Key 'video_m3u8' not found in the response.")
                return "Key 'video_m3u8' not found in the response.", 500
        else:
            print("[ERROR] Response content type is not 'application/json'.")
            return "Response content type is not 'application/json'.", 500
    else:
        print("[ERROR] Channel not found.")
        return "Channel not found.", 404

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
