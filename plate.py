import time
import datetime
import openalpr_api
from openalpr_api.rest import ApiException
from pprint import pprint
from sinesp_client import SinespClient

now = datetime.datetime.now()
sc = SinespClient()

def get_plate(image_path):
    
    # create an instance of the API class
    api_instance = openalpr_api.DefaultApi()
    secret_key = 'sk_b3cf50efcc23dc5f8f11ad97' # str | The secret key used to authenticate your account.  You can view your  secret key by visiting  https://cloud.openalpr.com/ 
    country = 'br' # str | Defines the training data used by OpenALPR.  \"us\" analyzes  North-American style plates.  \"eu\" analyzes European-style plates.  This field is required if using the \"plate\" task  You may use multiple datasets by using commas between the country  codes.  For example, 'au,auwide' would analyze using both the  Australian plate styles.  A full list of supported country codes  can be found here https://github.com/openalpr/openalpr/tree/master/runtime_data/config 
    recognize_vehicle = 0 # int | If set to 1, the vehicle will also be recognized in the image This requires an additional credit per request  (optional) (default to 0)
    state = '' # str | Corresponds to a US state or EU country code used by OpenALPR pattern  recognition.  For example, using \"md\" matches US plates against the  Maryland plate patterns.  Using \"fr\" matches European plates against  the French plate patterns.  (optional) (default to )
    return_image = 0 # int | If set to 1, the image you uploaded will be encoded in base64 and  sent back along with the response  (optional) (default to 0)
    topn = 10 # int | The number of results you would like to be returned for plate  candidates and vehicle classifications  (optional) (default to 10)
    prewarp = '' # str | Prewarp configuration is used to calibrate the analyses for the  angle of a particular camera.  More information is available here http://doc.openalpr.com/accuracy_improvements.html#calibration  (optional) (default to )

    # 1 = single car
    try:
        # call api
        api_response = api_instance.recognize_file(image_path, secret_key, country, recognize_vehicle=recognize_vehicle, state=state, return_image=return_image, topn=topn, prewarp=prewarp)
        print(api_response.results[0].plate)
        try:
            # sucessful plate recognition
            plate = api_response.results[0].plate
            file_name = now.strftime("%Y-%m-%d") + '_logs.csv'
            with open('logs/' + file_name, 'a') as file:
                time = now.strftime("%Y-%m-%d %H:%M")
                columns = [time, plate] + get_car_info(plate)
                line = ','.join(column for column in columns) + '\n'
                file.write(line)
            return plate
        except:
            # fail plate recognition
            print('-> Fail Plate Recognition')
            return 'Fail'
    except ApiException as e:
        print ("Exception when calling DefaultApi> recognize_file: %s\n" % e)

def get_car_info(plate):
    result = sc.search(plate)
    return [result['status_message'], result['chassis'], result['model'], result['brand'], result['color'], result['year'], result['city'], result['state'],]
