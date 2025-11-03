import httpx
from bs4 import BeautifulSoup


async def fetch_page(url: str) -> str:
    """Fetch the content of a web page asynchronously."""
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

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(teacher_parser("Razzaque"))