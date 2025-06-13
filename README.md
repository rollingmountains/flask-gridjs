**This project is based on Miguel Grinberg's book SQLACHEMY 2.0.**

**Project:** This project uses the gridjs library to present data in a table format. The backend provides data based on search criteria and other parameters, such as the sorting column and the length per page. 
**DB Design:** The complexity is at an intermediate level. Primary entities are Customer and Product. Both have an association with Orders and Product reviews by Customer. An additional feature includes Blog Articles(tied to Product articles and non-Product articles), which have an association with Blog views. The articles have also been expanded to have an association with translation. A bit of granularity is introduced in Blog views, which has an association with views by Customer or anonymous user.
**DB Diagram**
![Customer and Product](https://github.com/user-attachments/assets/6965facb-81fb-49dd-99cd-476766ca6898)

**Tech stack for this project:**
1. Flask for backend
2. SQLALCHEMY to design db architecture
3. GridJS for frontend
4. Relationship diagram using dbdiagram.io
