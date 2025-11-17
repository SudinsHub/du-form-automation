import httpx
from bs4 import BeautifulSoup


async def fetch_page(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

async def teacher_parser(query: str):
    plus_query = query.replace(" ", "+")
    url = f"https://du.ac.bd/find_web?search_type=people&search={plus_query}"
    html_doc = await fetch_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    fetched_teachers = soup.find('div', id='showData').find_all('div', class_='item')
    found_teachers = []
    for teacher in fetched_teachers:
        url = teacher.find('a')['href'].split('/')
        code = url[-2]+ "-" +url[-1]
        objs = teacher.find_all('h4')
        name = objs[0].text.strip()
        dept = objs[1].text.strip()
        designation = teacher.find('span').text.strip()
        print(f"Name: {name}, Department: {dept}, Designation: {designation}, Code: {code}")
        found_teachers.append({
            "name": name,
            "department": dept,
            "designation": designation,
            "code": code
        })

    return found_teachers

async def department_parser():
    url = f"https://www.du.ac.bd/departments"
    html_doc = await fetch_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')


    fetched_depts = soup.find('div', id='show_result').find_all('div', class_='info')
    found_dept = []
    for dept in fetched_depts:
        url = dept.find('h4').find('a')
        dept_code = url['href'].split('/')[-1]
        dept_name = url.text.strip()
        print(f"Department: {dept_name}, Code: {dept_code}")
        found_dept.append({
            "name": dept_name,
            "code": dept_code
        })
    return found_dept

async def course_parser(dept_code: str):
    url = f"https://du.ac.bd/undergrad/{dept_code}"
    html_doc = await fetch_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')

    fetched_semesters = soup.find('div', class_='tab-content').find('div', id='tab2').find_all('div', id='headingOne')
    fetched_courses = soup.find('div', class_='tab-content').find('div', id='tab2').find_all('div', attrs={'aria-labelledby': 'headingOne'})
    
    for semester_div, course_div in zip(fetched_semesters, fetched_courses):
        semester_name = semester_div.find('a').text.strip()
        print(f"Semester: {semester_name}")
        courses = course_div.find_all('div', class_='title')
        for course in courses:
            course_info = course.text.strip().split('|')
            course_code = course_info[0].strip()
            course_code = course_code[3:].strip() if course_code[0:3] == 'N/A' else course_code
            course_name = course_info[1].strip()
            credits = course_info[2].strip().split(' ')[0].strip()
            print(f"  Course: {course_name}, Code: {course_code}, Credits: {credits}")
    # return found_courses

if __name__ == "__main__":
    import asyncio
    asyncio.run(course_parser("CSE"))

    