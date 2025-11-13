# Bookify

Bookify is a web-based application designed to allow users to discover, browse, and reserve tables at restaurants through a simple and intuitive interface. The platform provides a clean homepage that offers quick access to the main user actions, including sign-up, log-in, and browsing options. Each user role, namely Owner, Customer, and Admin, has access to a dedicated dashboard with personalized functionality and a clear navigation structure that enhances the overall user experience.

The project aims to establish a complete restaurant booking and management system that integrates essential functionalities such as role-based dashboards, table reservations, real-time queue management, and reservation confirmations. The interface is structured to be responsive and user-friendly, ensuring accessibility and ease of use across various devices. The design philosophy emphasizes scalability, maintainability, and a clean separation between the front-end presentation and back-end logic.


To run Bookify locally on macOS or Linux, the user should begin by cloning the repository using the command  
`git clone https://github.com/eligeabiantoun/bookify.git`  
and then navigate into the project directory using `cd bookify`. A virtual environment must then be created and activated with  
`python3 -m venv venv`  
followed by  
`source venv/bin/activate`.  
Once activated, dependencies can be installed using  
`pip install -r requirements.txt`.  
After installing all dependencies, the user should apply database migrations with  
`python3 manage.py migrate`  
and start the local development server by executing  
`python3 manage.py runserver`.  
The application can then be accessed in a web browser at http://127.0.0.1:8000/.

The Bookify application is developed using the Django framework in Python for the backend and utilizes HTML and CSS for the front-end design, with future plans to integrate Tailwind CSS for improved visual consistency and responsiveness. The project uses SQLite as the default database for local development and PostgreSQL for production environments. Version control is managed through Git and GitHub to ensure structured collaboration and seamless tracking of development progress. The development workflow is primarily executed on macOS systems.

Bookify represents the foundation of a scalable, feature-rich restaurant booking platform that emphasizes structured design, clarity, and effective collaboration. It is being developed as part of a broader roadmap that envisions continuous improvement, advanced analytics, and integration of modern web technologies. The project reflects the team’s commitment to creating a practical solution that aligns technical precision with user-centric design.

Collaborators: Natalio Hassoun, Rasha Al Annan, Elige Abi Antoun, Elodie El Feghali, and Ralph Nasr.

Thank you for exploring Bookify.

