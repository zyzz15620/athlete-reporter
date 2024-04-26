import mysql.connector
import matplotlib.pyplot as plt
import textwrap
from docxtpl import DocxTemplate, InlineImage
import jinja2
import os
import numpy as np

MARTIAL=["pencaksilat","karate","muay","kickboxing","boxing","taekwondo","traditional martial art","vovinam","wushu"]

def ReadMySQL(discip):
	mydb = mysql.connector.connect(
	host="localhost",
	user="user",
	password="angel123",
	database="athlete_data"
	)

	mycursor = mydb.cursor()

	# get_first_set = f"select discipline, vn_discipline, level, name, sex, birth, start_training, height_cm, weight_kg, bodyfat_percent, cmj_cm, shouder_flexibility, 2arm_length_cm, 1arm_length_cm, h_length_cm, hand_length_cm, hand_width_cm, vital_capacity_lit, knee_chest_push_3kg, grip_kg, t_test_s, run_10m_s, run_20m_s, 5kg_overhead_throw, balance_left_s, balance_right_s, back_force_kg, leg_force_kg, batak_pro_60s, seat_reach_cm, beep_m, beep_vo2max, record_date from athlete_data.record_data where name = 'Tạ Nguyễn Minh Hùng' and discipline = '{discip}';" # thử riêng

	get_first_set = f"select discipline, vn_discipline, level, name, sex, birth, start_training, height_cm, weight_kg, bodyfat_percent, cmj_cm, shouder_flexibility, 2arm_length_cm, 1arm_length_cm, h_length_cm, hand_length_cm, hand_width_cm, vital_capacity_lit, knee_chest_push_3kg, grip_kg, t_test_s, run_10m_s, run_20m_s, 5kg_overhead_throw, balance_left_s, balance_right_s, back_force_kg, leg_force_kg, batak_pro_60s, seat_reach_cm, beep_m, beep_vo2max, record_date from athlete_data.record_data where year(record_date) = '2023' and discipline = '{discip}' and name in (select name from athlete_data.record_data where discipline = '{discip}' group by name having count(*) = 1);"
	
	mycursor.execute(get_first_set)

	first_set = mycursor.fetchall() # chứa những người cần làm z score
	print(discip)
	
	for i in range(len(first_set)):
		is_lack = False
		discipline, vn_dis, level, name, sex, birth, train, height, weight, fat, cmj, shouder, two_arm, one_arm, leg, hand_len, hand_wid, vc, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, seat, m, vo2max, record_date = first_set[i]
		first_set[i] =  process_data(first_set[i])
	
		if discipline in MARTIAL:
			get_name_set = f"select distinct name from athlete_data.record_data where sex = '{sex}' and birth between {birth} - 1 and {birth} + 1 and level = '{level}' and discipline in ('pencaksilat','karate','muay','kickboxing','boxing','taekwondo','traditional martial art','vovinam','wushu');"
			# get_name_set = f"select distinct name from athlete_data.record_data where sex = '{sex}' and level = '{level}' and discipline in ('pencaksilat','karate','muay','kickboxing','boxing','taekwondo','traditional martial art','vovinam','wushu');" # riêng cho những đứa không đủ
		else:
			get_name_set = f"select distinct name from athlete_data.record_data where sex = '{sex}' and level = '{level}' and discipline = '{discipline}';"
			# get_name_set = f"select distinct name from athlete_data.record_data where discipline = '{discipline}' and sex = '{sex}';" # riêng


		mycursor.execute(get_name_set)

		name_set = mycursor.fetchall()
		if len(name_set) < 4:
			print(name, len(name_set)-1)
			is_lack = True
			print_word_z(first_set[i], is_lack)
			continue
		print(name, len(name_set)-1)

		each_set = [] # chứa dữ liệu để tính z score cho từng cá nhân
		for each_name in name_set:
			get_data_set = f"select vital_capacity_lit, shouder_flexibility, seat_reach_cm, cmj_cm, knee_chest_push_3kg, grip_kg, t_test_s, run_10m_s, run_20m_s, 5kg_overhead_throw, balance_left_s, balance_right_s, back_force_kg, leg_force_kg, batak_pro_60s, beep_vo2max from athlete_data.record_data where name = '{each_name[0]}' order by record_date desc limit 1;"
			mycursor.execute(get_data_set)
			data_set = mycursor.fetchall()
			each_set.append(data_set[0])

		compare_set = process_each_set(each_set)
		main_set = [vc, shouder, seat, cmj, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, vo2max]

		z_score = calculate_zscore(main_set, compare_set)
		draw_chart_z(name, z_score)
		print_word_z(first_set[i], is_lack)

def print_word_z(first_set, is_lack):
	
	discipline, vn_dis, level, name, sex, birth, train, height, weight, fat, cmj, shouder, two_arm, one_arm, leg, hand_len, hand_wid, vc, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, seat, m, vo2max, record_date = first_set
	
	temp = discipline
	if temp in MARTIAL:
		temp = 'võ'

	template = DocxTemplate(f'C:/Users/VIETCONS/OneDrive/Máy tính/AUTO REPORT/report/mẫu báo cáo/z/{level}-{temp}-z.docx')
	
	if is_lack:
		chart_image = "Không đủ số liệu"
	else:
		chart_image_path = (f"{name}.png")
		chart_image = InlineImage(template, image_descriptor=chart_image_path)

	context = {
	'discipline': vn_dis.upper(),
	'level': level.upper(),
	'name': name,
	'sex': sex,
	'birth': birth,
	'height':height,
	'weight': weight,
	'train':train,
	'record': record_date,
	'vc':vc,
	'f': fat,
	'tarm': two_arm,
	'oarm': one_arm,
	'leg': leg,
	'shou': shouder,
	'hl': hand_len,
	'hw': hand_wid,
	'm': m,
	'lf': leg_force,
	'bf': back_force,
	'grip': grip,
	'cmj': cmj,
	'kneel': kneel,
	'run': run_10m,
	'runx2': run_20m,
	'ttest':t_test,
	'bal':balance_left,
	'bar':balance_right,
	'seat': seat,
	'batak': batak,
	'vo': vo2max,
	'throw': five_kg_overhead_throw,
	'chart': chart_image
	}

	jinja_env = jinja2.Environment(autoescape=True)
	template.render(context, jinja_env)

	template.save(f'C:/Users/VIETCONS/OneDrive/Máy tính/AUTO REPORT/report/báo cáo Z/{discipline} {level}/{name}_{level}_{discipline}_BÌNH DƯƠNG.docx') # chỉnh đường dẫn vào thư mụcC:\Users\VIETCONS\OneDrive\Máy tính\AUTO REPORT\report\báo cáo

	try:
		if os.path.exists(chart_image_path):
			os.remove(chart_image_path)
	except:
		pass

def draw_chart_z(name, data):
	plt.clf()
	column_name = []
	data_array = []

	for i in range(len(data)):
		column_name.append(data[i][0])
		data_array.append(data[i][1])

	column_name = [ '\n'.join(textwrap.wrap(cat, width=10)) for cat in column_name ]

	plt.rcParams['font.family']='Times New Roman'
	plt.figure(figsize=(7,3.8))
	# ax = plt.subplots()
	bars = plt.bar(column_name, data_array)
	plt.grid(axis='y')
	plt.gca().set_axisbelow(True)

	for spine in plt.gca().spines.values():
		spine.set_visible(False)

	for bar in bars:
		yval = bar.get_height()
		yval = round(yval, 2)
		if yval > 0:
			plt.text(bar.get_x() + bar.get_width()/2.0, yval, str(yval), va='bottom', ha='center')
		else:
			plt.text(bar.get_x() + bar.get_width()/2.0, yval, str(yval), va='top', ha='center')

	plt.tick_params(axis='x', labelsize=6.5)

	plt.title(name)
	plt.savefig(f'{name}.png', dpi=300)
	plt.close()

def calculate_zscore(main_set, compare_set):

	zscore = []

	vc, shouder, seat, cmj, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, vo2max = main_set

	vc_array=['Dung tích sống (lít)',1,vc]
	shouder_array=['Độ dẻo gập vai (cm)', 1,shouder]
	seat_array=['Ngồi với (cm)', 1, seat]
	cmj_array=['Bật nhảy đánh tay CMJ (cm)', 1, cmj]
	kneel_array=['Quỳ gối đẩy bóng 3kg trước ngực (m)', 1, kneel]
	grip_array=['Lực bóp tay thuận (cm)', 1, grip]
	t_test_array=['T test (giây)', -1, t_test]
	run_10m_array=['Chạy 10m (giây)', -1, run_10m]
	run_20m_array=['Chạy 20m (giây)', -1, run_20m]
	five_kg_overhead_throw_array=['Ném bóng 3kg qua đầu (m)', 1, five_kg_overhead_throw]
	balance_left_array=['Thăng bằng trái (giây)', 1, balance_left]
	balance_right_array=['Thăng bằng phải (giây)', 1, balance_right]
	back_force_array=['Lực lưng (kg)',1, back_force]
	leg_force_array=['Lực chân (kg)', 1, leg_force]
	batak_array=['Phản xạ Batak Pro 60s (lần)', 1, batak]
	vo2max_array=['Beep test (VO2 max) (ml/kg/ph)', 1, vo2max]

	main_array = [vc_array, shouder_array, seat_array, cmj_array, kneel_array, grip_array, t_test_array, run_10m_array, run_20m_array, five_kg_overhead_throw_array, balance_left_array, balance_right_array, back_force_array, leg_force_array, batak_array, vo2max_array]

	for i in range(len(main_array)):
		x = main_array[i][2]
		mean = compare_set[i][0]
		std = compare_set[i][1]

		try:
			z = (x - mean)/std
			z *= main_array[i][1]
			z = round(z,2)
			zscore.append([main_array[i][0],z])

		except:
			continue
	
	return zscore

def cal_z(x, mean, std):
	z = (x - mean)/std
	return z
	
def process_each_set(each_set):
	compare_set = []
	convert_set = [[] for _ in range(16)] # 15 là vì có 15 chỉ số thể lực tất cả

	for tpl in each_set: # tạo các mảng chứa từng nhóm chỉ số
		for i in range(16):
			convert_set[i].append(tpl[i])
	
	for i in range(len(convert_set)): # loại bỏ None khỏi mảng
		clean = [x for x in convert_set[i] if x is not None]
		convert_set[i] = clean

	for i in range(len(convert_set)):
		try:
			mean = np.mean(convert_set[i])
			std = np.std(convert_set[i])
		except:
			mean = None
			std = None
		compare_set.append([mean,std])

	return compare_set

def process_data(data):
	data = list(data)
	for i in range(len(data)):
		if data[i] is None:
			data[i] = "-"

	# process_to_draw_chart_z(kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, seat, vo2max)

	discipline, vn_dis, level, name, sex, birth, start_training, height, weight, fat, cmj, shouder, two_arm, one_arm, leg, hand_len, hand_wid, vc, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, seat, m, vo2max, date = data

	
	# micursor = mydb.cursor()
	# micursor.execute(get_name_set)
	# name_set = mycursor.fetchall()
	# print(name_set)
	
	if vn_dis == "-":
		vn_dis = discipline

	vn_dis = vn_dis + " tỉnh bình dương"

	if sex == "M":
		sex = "Nam"
	elif sex == "F":
		sex = "Nữ"

	record_date = date.strftime('%m-%Y')
	train = int(date.strftime('%Y'))-start_training

	if train == 0:
		train = "-"

	data = [discipline, vn_dis, level, name, sex, birth, train, height, weight, fat, cmj, shouder, two_arm, one_arm, leg, hand_len, hand_wid, vc, kneel, grip, t_test, run_10m, run_20m, five_kg_overhead_throw, balance_left, balance_right, back_force, leg_force, batak, seat, m, vo2max, record_date]
	
	return data





all_discipline = []
for i in all_discipline:
	ReadMySQL(i)
	# ["traditional martial art","pencaksilat","karate","muay","kickboxing","boxing","vovinam","wushu","taekwondo","judo","cycling","swim","football","table tennis","archery","track and field","volleyball"] pencaksilat, boxing , cycling(cấm), karate(cấm), archery(cấm), volleyball(cấm), taekwondo(cấm), swim(cấm)
