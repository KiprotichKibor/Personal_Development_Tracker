# Waweza: Your Personal Development Companion 🌱


![Screenshot (250)](https://github.com/user-attachments/assets/e3fdc2e7-31b3-4780-a1a0-38e24d3e8e4d)


## The Story Behind Waweza 📖

Waweza, which means "You Can" in Swahili, was born out of a personal struggle with consistency in self-improvement. As a student in Kenya, I often found myself and my peers starting strong with our goals, only to lose motivation over time. This project is my attempt to solve this universal challenge.

The spark for Waweza came during a particularly challenging semester when I decided to meticulously track my habits, moods, and progress in a simple notebook. The insights I gained were transformative, revealing clear connections between my moods, habits, and productivity.

With Waweza, I aim to digitize and enhance this process, making personal development more accessible, data-driven, and ultimately, more effective for everyone.

**Authors:**
- Kiprotich Kibor - https://www.linkedin.com/in/kiprotich-kibor/
- Kevin Gatamu - https://www.linkedin.com/in/kevingatamu/

## Features and Technical Challenges 🛠️

### 1. Goal Setting and Habit Tracking
Users can set personal goals and track daily habits. We implemented this using a relational database structure, linking users, goals, and habit entries.

**Technical Challenge:** Designing a flexible schema that allows for various goal types and habit frequencies while maintaining data integrity.

### 2. Mood Logging and Real-time Analytics 📊
One of our most challenging and rewarding features. Users can log their moods throughout the day, which are then correlated with their productivity and goal progress.

**Technical Deep Dive:** Initially, we updated analytics in real-time with each mood entry, but this caused performance issues. Our solution involved:
1. Implementing a Redis queue to buffer mood entries
2. Using Celery for asynchronous processing of entries
3. Updating analytics at regular intervals

This approach required diving into asynchronous programming and message queues, concepts that were new to us. We faced challenges with race conditions and data consistency, but the final implementation significantly improved performance and scalability.

### 3. Responsive Design 📱
Waweza is fully responsive, ensuring a seamless experience across devices.

**Implementation:** We used Bootstrap for its grid system and responsive utilities, customizing components to fit our unique design. Media queries were employed for fine-tuned control over the layout at different breakpoints.

### 4. User Authentication and Security 🔒
We implemented a robust authentication system with email verification and password reset functionality.

**Security Measures:**
- Passwords are hashed using bcrypt
- HTTPS enforced across the application
- CSRF protection on all forms
- Rate limiting on sensitive endpoints to prevent brute-force attacks

## The Tech Stack 🥞

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Backend:** Flask (Python), SQLAlchemy
- **Database:** SQLite (for MVP phase)
- **Server:** Nginx, Gunicorn
- **Additional Tools:** Redis, Celery for asynchronous tasks

## Installation and Setup 🚀

Just visit www.waweza.org when you can sign up and start all for free!

## Challenges and Learnings 🧠

1. **Asynchronous Programming:** Implementing real-time mood tracking pushed us to learn about asynchronous programming and message queues. This was a steep learning curve but incredibly rewarding.

2. **Data Visualization:** Creating meaningful and interactive charts was challenging. We explored various libraries before settling on Chart.js for its balance of features and ease of use.

3. **User Experience:** Balancing feature richness with simplicity was an ongoing challenge. We learned the importance of user testing and iterative design.

## Future Enhancements 🚀

1. **Machine Learning Integration:** We aim to implement predictive analytics to provide personalized insights and recommendations.

2. **Social Features:** A community aspect where users can share goals and support each other, while maintaining privacy.

3. **API Development:** Creating a public API to allow integration with other health and productivity apps.


## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 👏

- Our mentors at alx_se for their guidance
- The open-source community for the amazing tools and libraries
- Our beta testers for their invaluable feedback

---

Waweza is more than just a project; it's a testament to the power of personal growth and the impact technology can have on our lives. We hope it inspires and aids you in your own journey of self-improvement. Remember, with Waweza, you can! 💪
