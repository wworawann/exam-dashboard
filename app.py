import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Exam Tracking Dashboard", layout="wide")
st.title("📊 Dashboard ติดตามการสอบ")

# โหลดข้อมูล
@st.cache_data
def load_data():
    df = pd.read_csv("Exam_Tracking_Data_Detail_Tabl.csv")
    df['Exam Date'] = pd.to_datetime(df['Exam Date'])
    return df

df = load_data()

# --- ส่วนของการกรองข้อมูล (Filters) ---
st.sidebar.header("🔍 กรองข้อมูลตามเงื่อนไข")

# กรองตามชื่อเด็ก (แยกชื่อจาก comma)
all_children = set([child.strip() for names in df['Child Name'].dropna() for child in names.split(',')])
selected_child = st.sidebar.multiselect("เลือกชื่อนักเรียน:", options=list(all_children), default=list(all_children))

# กรองตามสถานะ
all_status = df['status'].unique()
selected_status = st.sidebar.multiselect("เลือกสถานะการสอบ:", options=all_status, default=all_status)

# ฟังก์ชันกรองข้อมูล
def filter_data(data):
    # กรองสถานะ
    filtered = data[data['status'].isin(selected_status)]
    # กรองชื่อเด็ก
    if selected_child:
        mask = filtered['Child Name'].apply(lambda x: any(child in x for child in selected_child))
        filtered = filtered[mask]
    return filtered

filtered_df = filter_data(df)

# --- ส่วนการแสดงผล (Visualizations) ---
col1, col2, col3 = st.columns(3)
col1.metric("จำนวนสนามสอบทั้งหมด (ตามตัวกรอง)", len(filtered_df))
col2.metric("สอบเสร็จแล้ว (Done)", len(filtered_df[filtered_df['status'] == 'Done']))
col3.metric("รอสอบ (Waiting)", len(filtered_df[filtered_df['status'] == 'Waiting']))

st.markdown("---")

col_chart1, col_chart2 = st.columns(2)

# Chart 1: สัดส่วนสถานะการสอบ
with col_chart1:
    st.subheader("สัดส่วนสถานะการสอบ")
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_status = px.pie(status_counts, values='Count', names='Status', color='Status', 
                        color_discrete_map={'Waiting':'#FFA07A', 'Done':'#90EE90'})
    st.plotly_chart(fig_status, use_container_width=True)

# Chart 2: ไทม์ไลน์การสอบ
with col_chart2:
    st.subheader("กำหนดการสอบ (Timeline)")
    
    # สร้างคอลัมน์ใหม่สำหรับแปลงวันที่ให้อยู่ในรูปแบบที่อ่านง่ายขึ้น เช่น '06-Sep'
    filtered_df['Date Label'] = filtered_df['Exam Date'].dt.strftime('%d-%b')
    
    fig_timeline = px.scatter(filtered_df, x="Exam Date", y="Exam/Project", color="status", 
                              text="Date Label", # เพิ่มบรรทัดนี้เพื่อบอกให้เอาคอลัมน์ Date Label มาแสดงเป็นข้อความ
                              hover_data=["Child Name", "Subjects", "Venue"], size_max=60)
    
    # เพิ่ม textposition='top center' เพื่อให้ข้อความลอยอยู่ด้านบนของจุดกราฟ จะได้ไม่บังจุด
    fig_timeline.update_traces(marker=dict(size=15), textposition='top center')
    
    # (ทางเลือก) ปรับให้แกน Y กว้างขึ้นนิดหน่อย ข้อความจะได้ไม่โดนตัดตรงขอบบน
    fig_timeline.update_layout(margin=dict(t=30))
    
    st.plotly_chart(fig_timeline, use_container_width=True)
# ตารางแสดงข้อมูลรายละเอียด
st.subheader("📋 รายละเอียดข้อมูลการสอบ")
st.dataframe(filtered_df[['Exam/Project', 'Child Name', 'Subjects', 'Exam Date', 'Venue', 'status']], use_container_width=True)
