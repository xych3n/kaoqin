# KaoQin (考勤) Management System

KaoQin is a modern attendance management system designed to replace the outdated and user-unfriendly existing system.
The project employs the `fastapi` framework as the backend and utilizes the `quasar` framework for the frontend.

## Introduction

The "KaoQin" project, meaning "考勤" in Chinese, serves as an attendance management system that aims to improve the existing process for recording and managing activities and attendance records.
The previous system was outdated and inaccessible to the public, making it difficult for users to interact with it conveniently.
KaoQin provides a user-friendly web interface accessible through the campus network (which is, SUDA WiFi or SUDA VPN).

## Features

- **Seamless Self-Reflection:** Users can now freely view the list of activities they've participated in and keep track of their attendance count.

- **Smart Attendance Recording:** Administrators can mark attendance for specific activities or participants, with the system supporting variable attendance count. No need for multiple uploads or additional steps!

- **Flexible Attendance Modification:** The system allows administrators to easily delete or modify previously recorded attendance counts without the hassle of uploading additional files. Of course, the activity name, date, etc. can also be modified.

- **Automated Data Validation:** The system automatically validates data during attendance record entry, preventing issues such as incorrect student number inputs or duplicate entries for the same participant in the same activity.

- **Legacy System Data Access:** For users who may have specific data retrieval needs from the previous legacy system, this management system provides handy scripts to access the data. Although most relevant information has been migrated to the current system, these scripts ensure access to any remaining data as needed.

## Getting Started

To access the KaoQin Management System, open your web browser and navigate to the following URL: [http://10.20.7.127:5000](http://10.20.7.127:5000). Please log in using your student number as the login name and the last 6 digits of your ID card as the default password.

## Acknowledgments

- Special thanks to [pratik227](https://github.com/pratik227) for the inspiration from the [Quasar-Minimalist-Design](https://github.com/Quasar-Admin-Templates/Quasar-Minimalist-Design) repository. While the repository is closed source and paid, the visual design of this project was influenced by its design.

## Bug Reports and Feature Requests

If you encounter any issues or have specific feature requests, please [create an issue](https://github.com/Evlpsrfc/KaoQin/issues) on GitHub.

## Roadmap

The development and maintenance of this project are shared responsibilities between myself and the members of the Graduate Student Union. Both parties have the authority to contribute to the ongoing development and maintenance of this code repository.
I am committed to collaborating with the Graduate Student Union members and may actively participate in future maintenance and development tasks as needed. The project's continuity and evolution will depend on the mutual efforts and contributions of all involved parties.


## Contact Information

For any inquiries or feedback, feel free to contact me at my school email: 20225227002@stu.suda.edu.cn.
