import datetime, json
from haversine              import haversine

from account.my_utils       import requirelogin, logincheck
from .models                import *

from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models       import Avg
from django.db.models       import Q

class DetailView(View):
    def get(self, request):
        try:
            type = request.GET.get('type', None)
            id   = request.GET.get('id', None)
            if type == 'complex':
                complex = Complex.objects.select_related('complex_price_info').get(id = id)
                complex_detail = {
                    'complex_id'                        : id,
                    'complex_type'                      : complex.complex_type.name,
                    'address'                           : complex.address,
                    'location'                          : {"longitude" : complex.longitude, "latitude" : complex.latitude},
                    'name'                              : complex.name,
                    'enter_date'                        : complex.enter_date,
                    'household_num'                     : complex.household_num,
                    'parking_average'                   : complex.parking_average,
                    'building_num'                      : complex.building_num,
                    'heat_type'                         : complex.heat_type.name,
                    'fuel_type'                         : complex.fuel_type.name,
                    'provider_name'                     : complex.provider_name,
                    'lowest_floor'                      : complex.lowest_floor,
                    'highest_floor'                     : complex.highest_floor,
                    'entrance_type'                     : complex.entrance_type.name,
                    'build_cov_ratio'                   : complex.build_cov_ratio,
                    'floor_area_index'                  : complex.floor_area_index,
                    'image_urls'                        : [image.image_url for image in complex.compleximage_set.all()],
                    'trade_average_pyeong_price'        : (complex.complex_price_info.trade_average_pyeong_price),
                    'lease_average_pyeong_price'        : complex.complex_price_info.lease_average_pyeong_price,
                    'trade_region_average_pyeong_price' : complex.complex_price_info.trade_region_average_pyeong_price,
                    'lease_region_average_pyeong_price' : complex.complex_price_info.lease_region_average_pyeong_price,
                    'pyeong_infos' :[{
                        'complex_space_info_id'    : pyeong.id,
                        'pyeong_type'              : pyeong.pyeong_type,
                        'room_size'                : pyeong.room_size,
                        'provision_size'           : pyeong.provision_size,
                        'contract_size'            : pyeong.contract_size,
                        'maintenance_price'        : pyeong.maintenance_price,
                        'beds_num'                 : pyeong.beds_num,
                        'bath_num'                 : pyeong.bath_num,
                        'entrance_type'            : pyeong.entrance_type.name,
                        'lay_out_image_URL'        : pyeong.lay_out_image_URL,
                        'extend_lay_out_image_URL' : pyeong.extend_lay_out_image_URL
                        } for pyeong in complex.complexspaceinfo_set.all()]
                    }
                return JsonResponse({"complex_detail": complex_detail}, status = 200)
            
            elif type == 'room':
                room = (
                    Room
                    .objects
                    .select_related('room_add_info', 'score', 'agent', 'belonged_agent')
                    .get(id = id)
                )
                trade_info = (
                    TradeInfo
                    .objects
                    .filter(room_id = id)
                    .all()
                    .values('deposit', 'fee', 'trade_type_id__name')
                )

                room_detail = {
                    'room_id'           : id,
                    'room_type'         : room.room_type.name,
                    'room_sub_type'     : room.room_sub_type.name,
                    'is_confirmed'      : room.is_confirmed,
                    'confirmed_date'    : room.confirmed_date,
                    'is_short_lease'    : room.is_short_lease,
                    'title'             : room.title,
                    'description'       : room.description,
                    'room_size'         : room.room_size,
                    'provision_size'    : room.provision_size,
                    'contract_size'     : room.contract_size,
                    'room_floor'        : room.room_floor.name,
                    'building_floor'    : room.building_floor.name,
                    'maintenance_price' : room.maintenance_price,
                    'address'           : room.address,
                    'heat_type'         : room.heat_type.name,
                    'moving_date_type'  : room.moving_date_type.name,
                    'moving_date'       : room.moving_date,
                    'building_use'      : room.building_use.name if room.building_use else None,
                    'image_urls'        : [image.image_url for image in room.roomimage_set.all()],
                    'room_add_info'     : {
                        'is_builtin'    : room.room_add_info.is_builtin,
                        'is_elevator'   : room.room_add_info.is_elevator,
                        'is_pet'        : room.room_add_info.is_pet,
                        'is_balcony'    : room.room_add_info.is_balcony,
                        'is_loan'       : room.room_add_info.is_loan,
                        'is_parking'    : room.room_add_info.is_parking,
                        'parking_fee'   : room.room_add_info.parking_fee,
                    },
                    'score'             : {
                        'price'         : room.score.price if room.score else None,
                        'option'        : room.score.option if room.score else None,
                        'near'          : room.score.near if room.score else None,
                        'maintenance'   : room.score.maintenance if room.score else None,
                        'traffic'       : room.score.traffic if room.score else None,
                    },
                    'agent'             : {
                        'name'          : room.agent.name,
                        'face_name'     : room.agent.face_name,
                        'face_number'   : room.agent.face_number,
                        'address'       : room.agent.address,
                    },
                    'belonged_agent'    : {
                        'name'          : room.belonged_agent.name,
                        'phone_number'  : room.belonged_agent.phone_number,
                    },
                    'trade_infos'       : [
                        {
                            'trade_info_name'   : trade.get('trade_type_id__name'),
                            'deposit'           : trade.get('deposit'),
                            'fee'               : trade.get('fee')
                        } for trade in trade_info
                    ]
                }

                if room.complex:
                    room_detail['complex'] = {
                        'complex_id'        : room.complex.id,
                        'complex_name'      : room.complex.name,
                        'enter_date'        : room.complex.enter_date,
                        'household_num'     : room.complex.household_num,
                        'parking_average'   : room.complex.parking_average
                    }
                    pyeong_infos = (
                        room
                        .complex
                        .complexspaceinfo_set.filter(
                            room_size = room.room_size,
                            provision_size = room.provision_size
                        )
                    )
                    room_detail['pyeong_infos'] = [{
                            'complex_space_info_id'    : pyeong.id,
                            'beds_num'                 : pyeong.beds_num,
                            'bath_num'                 : pyeong.bath_num,
                            'entrance_type'            : pyeong.entrance_type.name,
                            'lay_out_image_URL'        : pyeong.lay_out_image_URL,
                    } for pyeong in pyeong_infos]

                return JsonResponse({"room_detail" : room_detail}, status = 200)
            
            return HttpResponse(status = 400)
        
        except Complex.DoesNotExist:
            return JsonResponse({"message": "INVALID_COMPLEX_ID"}, status = 400)
        
        except Room.DoesNotExist:
            return JsonResponse({"message" : "INVALID_ROOM_ID"}, status = 400)

class TradeHistoryView(View):
    def get(self, request):
        try:
            id                = request.GET.get('id', None)
            now               = datetime.datetime.now().strftime('%Y%m')
            three_year_before = f'{int(now[:4])-3}{now[4:]}'
            pyeong            = (
                ComplexSpaceInfo
                .objects
                .prefetch_related('tradehistory_set')
                .get(id = id)
            )

            rent_month            = [date_dict['date'] for date_dict in pyeong.tradehistory_set
                                     .filter(date__gte = three_year_before, trade_type_id = 1)
                                     .values('date').distinct()]
            monthly_rent_lists    = [pyeong
                                     .tradehistory_set
                                     .filter(date = date, trade_type_id = 1)
                                      for date in rent_month]

            lease_month           = [date_dict['date'] for date_dict in pyeong.tradehistory_set
                                     .filter(date__gte = three_year_before, trade_type_id = 2)
                                     .values('date').distinct()]
            monthly_lease_lists   = [pyeong
                                     .tradehistory_set
                                     .filter(date = date, trade_type_id = 2)
                                      for date in lease_month]

            selling_month         = [date_dict['date'] for date_dict in pyeong.tradehistory_set
                                     .filter(date__gte = three_year_before, trade_type_id = 3)
                                     .values('date').distinct()]
            monthly_selling_lists = [pyeong
                                     .tradehistory_set
                                     .filter(date = date, trade_type_id = 3)
                                      for date in selling_month]

            results = {
                'rent_history' : [{
                    'date'            : monthly_rent[0].date,
                    'rent_count'      : monthly_rent.count(),
                    'histories'       : [{
                        'type'    : rent.trade_type.name,
                        'date'    : rent.date,
                        'deposit' : rent.deposit,
                        'price'   : rent.price,
                        'floor'   : rent.floor
                        } for rent in monthly_rent]
                    } for monthly_rent in monthly_rent_lists],
                'lease_history' : [{
                    'date'            : monthly_lease[0].date,
                    'lease_count'     : monthly_lease.count() ,
                    'average_deposit' : int(monthly_lease.aggregate(Avg('deposit'))['deposit__avg']),
                    'histories'       : [{
                        'type'    : lease.trade_type.name,
                        'date'    : lease.date,
                        'deposit' : lease.deposit,
                        'floor'   : lease.floor
                        } for lease in monthly_lease]
                    } for monthly_lease in monthly_lease_lists],
                'selling_history' : [{
                    'date'            : monthly_selling[0].date,
                    'selling_count'   : monthly_selling.count(),
                    'average_deposit' : int(monthly_selling.aggregate(Avg('deposit'))['deposit__avg']),
                    'histories'       : [{
                        'type'    : selling.trade_type.name,
                        'date'    : selling.date,
                        'deposit' : selling.deposit,
                        'floor'   : selling.floor
                        } for selling in monthly_selling]
                    } for monthly_selling in monthly_selling_lists]
                }
            return JsonResponse({"result":results}, status = 200)
        except ComplexSpaceInfo.DoesNotExist:
            return JsonResponse({"message":"INVALID_COMPLEXSPACEINFO_ID"}, status = 400)

class NearInfoView(View):
    def get(self, request):
        try:
            longitude = float(request.GET.get('longitude', None))
            latitude  = float(request.GET.get('latitude', None))
            position  = (latitude,longitude)
            condition = (
                Q(latitude__range  = (latitude - 0.01, latitude + 0.01)) | 
                Q(longitude__range = (longitude - 0.015, longitude + 0.015))
            )

            convenience_infos = (
                ConvenienceInfo
                .objects
                .filter(condition)
            )
            near_convenience_infos = [info for info in convenience_infos
                                      if haversine(position, (info.latitude, info.longitude)) <= 2]

            safety_infos = (
                SafetyInfo
                .objects
                .filter(condition)
            )
            near_safety_infos = [info for info in safety_infos
                                 if haversine(position, (info.latitude, info.longitude)) <= 2]

            education_infos = (
                EducationInfo
                .objects
                .filter(condition)
            )
            near_education_infos = [info for info in education_infos
                                    if haversine(position, (info.latitude, info.longitude)) <= 2]

            results = {
                "convenience" : {
                    "subway" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_convenience_infos
                        if info.convenience_category_id == 1],
                    "convenient_store" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_convenience_infos
                        if info.convenience_category_id == 2],
                    "bank" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_convenience_infos
                        if info.convenience_category_id == 4],
                    "mart" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_convenience_infos
                        if info.convenience_category_id == 6],
                    "pharmacy" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_convenience_infos
                        if info.convenience_category_id == 7]
                    },
                "safety" : {
                    "police" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_safety_infos
                        if info.safety_category_id == 1],
                    "cctv" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_safety_infos
                        if info.safety_category_id == 2]
                    },
                "education" : {
                    "nursery_school" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_education_infos
                        if info.education_category_id == 1],
                    "kinder_school" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_education_infos
                        if info.education_category_id == 2],
                    "elementary_school" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_education_infos
                        if info.education_category_id == 3],
                    "middle_school" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_education_infos
                        if info.education_category_id == 4],
                    "high_school" : [{
                        "name" : info.name,
                        "position" : (float(info.latitude), float(info.longitude))
                        } for info in near_education_infos
                        if info.education_category_id == 5]
                    }
            }
            return JsonResponse({"results":results}, status = 200)
        except ValueError:
            return JsonResponse({"message":"INVALID_POSITION"}, status = 400)

class RoomUploadView(View):
    def get(self, request):
        room_info = {
            'room_type'        : list(RoomType.objects.values()),
            'trade_type'       : list(TradeType.objects.values()),
            'floor'            : list(Floor.objects.values()),
            'heat_type'        : list(HeatType.objects.values()),
            'moving_date_type' : list(MovingDateType.objects.values()),
            'room_sub_type'    : list(RoomSubType.objects.values())
        }
        return JsonResponse(room_info, status = 200)

    @requirelogin
    def post(self, request):
        data = json.loads(request.body)

        try:
            trade_infos   = data.get('trade_info')
            room_add_info = RoomAddInfo.objects.create(
                is_builtin  = data['is_builtin'],
                is_elevator = data['is_elevator'],
                is_pet      = data['is_pet'],
                is_balcony  = data['is_balcony'],
                is_loan     = data['is_loan'],
                is_parking  = data['is_parking'],
                parking_fee = data.get('parking_fee')
            )

            room = Room.objects.create(
                room_type_id        = data['room_type_id'],
                address             = data['address'],
                longitude           = data['longitude'],
                latitude            = data['latitude'],
                is_short_lease      = data.get('is_short_lease'),
                room_size           = data['room_size'],
                provision_size      = data.get('provision_size'),
                room_floor_id       = data.get('room_floor_id'),
                building_floor_id   = data.get('building_floor_id'),
                heat_type_id        = data.get('heat_type_id'),
                moving_date_type_id = data.get('moving_date_type_id'),
                moving_date         = data.get('moving_date'),
                room_add_info_id    = room_add_info.id,
                title               = data['title'],
                description         = data['description'],
                user_id             = request.user.id,
                is_maintenance_nego = data['is_maintenance_nego'],
                maintenance_price   = data.get('maintenance_price')
            )

            RoomImage.objects.create(
                image_url = data['image_url'],
                room_id   = room.id
            )

            for trade_info in trade_infos:
                TradeInfo.objects.create(
                    trade_type_id = trade_info['trade_type_id'],
                    deposit       = trade_info['deposit'],
                    fee           = trade_info.get('fee'),
                    room_id       = room.id
                )
            
            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status = 400)

class FilteredRoomListView(View):
    @logincheck
    def get(self, request):
        try:
            offset    = int(request.GET.get('offset', None)) - 1
            limit     = int(request.GET.get('limit', None)) 
            zoom      = int(request.GET.get('zoom', None))
            longitude = float(request.GET.get('longitude', None))
            latitude  = float(request.GET.get('latitude', None))
            position  = (latitude,longitude)
            # base_range = 2 -> 상하좌우 각 1 km
            base_range = 2

            # 방 종류(원룸 / 투쓰리룸 / 오피스텔 / 아파트)
            multi_room_type   = request.GET.getlist('multi_room_type', None)
            # 매물 종류(월세 / 전세 / 매매)
            selling_type      = request.GET.getlist('selling_type', None)
            selling_type_int  = [int(type) for type in selling_type]
            deposit_range     = request.GET.getlist('deposit_range', None)
            fee_range         = request.GET.getlist('fee_range',  None)
            room_size         = request.GET.getlist('room_size', None)
            maintenance_price = request.GET.getlist('maintenance_price', None)

            condition = (
                Q(latitude__range  = (latitude - 0.005 * base_range * zoom, latitude + 0.005 * base_range * zoom))
                & Q(longitude__range = (longitude - 0.008 * base_range * zoom, longitude + 0.008 * base_range * zoom))
                & Q(room_type_id__in = multi_room_type)
                & Q(room_size__range = (int(room_size[0]), int(room_size[1])))
                & Q(maintenance_price__range = (int(maintenance_price[0]), int(maintenance_price[1])))
                & Q(tradeinfo__deposit__range = (int(deposit_range[0]), int(deposit_range[1])))
                & Q(tradeinfo__fee__range = (int(fee_range[0]), int(fee_range[1])))
                & Q(tradeinfo__trade_type_id__in = selling_type_int)
            )

            conditioned_rooms = Room.objects.filter(condition).distinct()
            near_rooms        = [
                room for room in conditioned_rooms
                if haversine(position, (room.latitude, room.longitude)) <= base_range * zoom
            ]

            filtered_rooms = [{
                'is_like'           : (
                    RoomLike.objects
                    .filter(room_id = room.id, user_id = request.user.id)
                    .exists() 
                    if request.user 
                    else None
                ),
                'room_id'           : room.id,
                'is_quick'          : room.is_quick,
                'is_confirmed'      : room.is_confirmed,
                'confirmed_date'    : room.confirmed_date,
                'title'             : room.title,
                'image_url'         : room.roomimage_set.first().image_url,
                'room_type_str'     : room.room_type.name,
                'floor_str'         : room.room_floor.name,
                'room_size'         : room.room_size,
                'latitude'          : float(room.latitude),
                'longitude'         : float(room.longitude),
                'maintenance_price' : room.maintenance_price,
                'trade_type_str'    : (
                    TradeInfo.objects
                    .filter(room_id = room.id, trade_type_id__in = selling_type_int)
                    .last()
                    .trade_type.name
                ),
                'trade_deposit'     : (
                    TradeInfo
                    .objects
                    .filter(room_id = room.id, trade_type_id__in = selling_type_int)
                    .last()
                    .deposit
                ),
                'trade_fee'         : (
                    TradeInfo
                    .objects
                    .filter(room_id = room.id, trade_type_id__in = selling_type_int)
                    .last()
                    .fee
                ),
            } for room in near_rooms[offset:limit]]
            filtered_rooms.append({"room_count" : len(near_rooms)})
            return JsonResponse({"results":filtered_rooms}, status = 200)
        except TypeError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)
        except IndexError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)
        except ValueError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)

class RoomListView(View):
    # 클러스터 클릭 방찾기
    @logincheck
    def get(self, request):
        try:
            like         = request.GET.get('like')
            offset       = int(request.GET.get('offset', None)) - 1
            limit        = int(request.GET.get('limit', None))
            room_id      = request.GET.getlist('room_id', None)

            if like:
                room_id_list = [
                    room.id for room in Room
                    .objects
                    .filter(room_like = request.user.id)
                ]
            else:
                room_id_list = [int(id) for id in room_id]

            rooms = [{
                'is_like'           : (
                    RoomLike.objects
                    .filter(room_id = room.id, user_id = request.user.id)
                    .exists() 
                    if request.user 
                    else None
                ),
                'room_id'           : room.id,
                'is_quick'          : room.is_quick,
                'is_confirmed'      : room.is_confirmed,
                'confirmed_date'    : room.confirmed_date,
                'title'             : room.title,
                'image_url'         : room.roomimage_set.first().image_url,
                'room_type_str'     : room.room_type.name,
                'floor_str'         : room.room_floor.name,
                'room_size'         : room.room_size,
                'latitude'          : float(room.latitude),
                'longitude'         : float(room.longitude),
                'maintenance_price' : room.maintenance_price,
                'trade_type_str'    : (
                    TradeInfo
                    .objects
                    .filter(room_id = room.id)
                    .first()
                    .trade_type
                    .name
                ),
                'trade_deposit'     : (
                    TradeInfo
                    .objects
                    .filter(room_id = room.id)
                    .first()
                    .deposit
                ),
                'trade_fee'         : (
                    TradeInfo
                    .objects
                    .filter(room_id = room.id)
                    .first()
                    .fee
                ),
            } for room in [Room.objects.get(id = room_id) for room_id in room_id_list[offset:limit]]]
            rooms.append({"room_count" : len(rooms)})
            return JsonResponse({"results":rooms}, status = 200)
        except TypeError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)

class FilteredPositionListView(View):
    def get(self, request):
        try:
            zoom      = int(request.GET.get('zoom', None))
            longitude = float(request.GET.get('longitude', None))
            latitude  = float(request.GET.get('latitude', None))
            position  = (latitude,longitude)
            # base_range = 2 -> 상하좌우 각 1 km
            base_range = 2

            # 방 종류(원룸 / 투쓰리룸 / 오피스텔 / 아파트)
            multi_room_type   = request.GET.getlist('multi_room_type', None)
            # 매물 종류(월세 / 전세 / 매매)
            selling_type      = request.GET.getlist('selling_type', None)
            selling_type_int  = [int(type) for type in selling_type]
            deposit_range     = request.GET.getlist('deposit_range', None)
            fee_range         = request.GET.getlist('fee_range',  None)
            room_size         = request.GET.getlist('room_size', None)
            maintenance_price = request.GET.getlist('maintenance_price', None)

            condition = (
                Q(latitude__range  = (latitude - 0.005 * base_range * zoom, latitude + 0.005 * base_range * zoom))
                & Q(longitude__range = (longitude - 0.008 * base_range * zoom, longitude + 0.008 * base_range * zoom))
                & Q(room_type_id__in = multi_room_type)
                & Q(room_size__range = (int(room_size[0]), int(room_size[1])))
                & Q(maintenance_price__range = (int(maintenance_price[0]), int(maintenance_price[1])))
                & Q(tradeinfo__deposit__range = (int(deposit_range[0]), int(deposit_range[1])))
                & Q(tradeinfo__fee__range = (int(fee_range[0]), int(fee_range[1])))
                & Q(tradeinfo__trade_type_id__in = selling_type_int)
            )

            conditioned_rooms = Room.objects.filter(condition).distinct()
            near_rooms        = [
                room for room in conditioned_rooms
                if haversine(position, (room.latitude, room.longitude)) <= base_range * zoom
                ]

            filtered_rooms   = [{
                'room_id'           : room.id,
                'latitude'          : float(room.latitude),
                'longitude'         : float(room.longitude),
            } for room in near_rooms[:zoom * 1000]]
            return JsonResponse({"results":filtered_rooms}, status = 200)
        except TypeError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)
        except IndexError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)
        except ValueError:
            return JsonResponse({"message":"INVALID_QUERY_PARAMETERS"}, status = 400)

class RoomLikeView(View):
    @requirelogin
    def post(self, request):
        data = json.loads(request.body)
        
        try:
            room_check = RoomLike.objects.filter(room_id = data['id'])

            if room_check.exists():
                room_check.get().delete()
                return JsonResponse({'message': 'DELETED'}, status = 200)

            RoomLike.objects.create(room_id = data['id'], user_id = request.user.id)
            return JsonResponse({'message': 'SAVED'}, status = 200)

        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status = 400)
            
