# AI-First Development Reflection

This document addresses the reflection questions required by Appendix C.7 of the AiDD 2025 Capstone project requirements, reflecting on our experience using AI tools (primarily Cursor AI) throughout the development of the Campus Resource Hub application.

---

## 1. How did AI tools shape your design or coding decisions?

AI tools, particularly Cursor AI, significantly influenced our design and coding decisions throughout the project. The most impactful contributions were in architectural decisions and code structure. For instance, Cursor AI suggested the initial Data Access Layer (DAL) pattern implementation, which helped us maintain strict separation between controllers and database operations. This architectural guidance led to a more maintainable and testable codebase.

The AI also influenced our approach to the AI chatbot feature. When implementing context grounding (as required by Section 9), Cursor AI suggested integrating the Product Requirements Document (PRD) from `/docs/context/PM/PRD.txt` directly into the chatbot's context system. This not only met the requirement but also improved the chatbot's ability to provide accurate, project-aligned responses.

Additionally, AI tools helped us identify potential security issues early, such as suggesting parameterized queries for SQL injection prevention and proper CSRF token implementation. The AI's suggestions for error handling patterns and type hints improved code quality and maintainability.

However, we maintained human oversight throughout. Every AI suggestion was reviewed, tested, and often modified to fit our specific requirements. The AI served as a collaborative partner rather than an autonomous coder, helping us explore design options and catch potential issues before they became problems.

---

## 2. What did you learn about verifying and improving AI-generated outputs?

One of the most important lessons was that AI-generated code is a starting point, not a final solution. We learned to always verify AI suggestions against project requirements, test them thoroughly, and adapt them to our specific context. For example, when Cursor AI suggested the initial DAL structure, we enhanced it with proper error handling, type hints, and transaction management that weren't in the original suggestion.

We also learned the importance of understanding the "why" behind AI suggestions. Simply accepting AI-generated code without understanding its rationale can lead to technical debt. We made it a practice to ask follow-up questions, review the logic, and ensure the solution aligned with our architecture patterns (MVC + DAL).

Testing became even more critical when working with AI-generated code. We found that AI suggestions sometimes looked correct but had edge cases or subtle bugs. Our comprehensive test suite (unit tests, integration tests, security tests) helped catch these issues early.

We also learned to provide better context to AI tools. By maintaining well-structured documentation in `/docs/context/` and clear code comments, we found that AI tools could provide more relevant and accurate suggestions. This reinforced the importance of the "Context Pack" folder structure required by the project.

---

## 3. What ethical or managerial considerations emerged from using AI in your project?

Several ethical and managerial considerations emerged during AI-assisted development. First, there was the question of attribution and transparency. We addressed this by adding AI attribution comments to code files, documenting AI assistance in `dev_notes.md`, and being transparent about AI's role in our development process. This aligns with academic integrity requirements and professional best practices.

We also considered the ethical implications of AI-generated code in production systems. While AI tools can accelerate development, they can also introduce security vulnerabilities or biases if not carefully reviewed. We established a review process where all AI-generated code was examined by team members before integration, ensuring human oversight and accountability.

From a managerial perspective, we learned that AI tools change the skill requirements for developers. Rather than replacing developers, AI tools shift focus from writing boilerplate code to architectural thinking, problem-solving, and code review. This has implications for how teams are structured and how junior developers are mentored.

We also considered the "hallucination" problem—AI tools sometimes generate plausible-looking but incorrect code or documentation. This reinforced the need for thorough testing and verification processes. We found that AI tools are most effective when used as collaborative partners rather than autonomous agents.

Finally, we reflected on the accessibility of AI tools. While powerful, these tools require API access, subscriptions, or specific development environments. This could create disparities in development capabilities between teams or organizations with different resources.

---

## 4. How might these tools change the role of a business technologist or product manager in the next five years?

AI tools will fundamentally transform the roles of business technologists and product managers over the next five years. For business technologists, AI will shift focus from writing code to understanding business requirements, designing system architectures, and ensuring AI-generated solutions align with organizational goals. The ability to effectively prompt AI tools and verify their outputs will become a core skill.

Product managers will need to become more technical, understanding not just what AI can do, but how to guide AI-assisted development to meet business objectives. They'll need to work more closely with development teams to provide context that helps AI tools generate better solutions. The `/docs/context/` folder structure we implemented demonstrates this—product managers will need to maintain rich context materials that help AI tools understand business goals, user personas, and success metrics.

We anticipate that AI tools will enable faster prototyping and iteration, allowing product managers to test ideas more quickly. However, this also means product managers will need stronger technical judgment to evaluate AI-generated solutions and ensure they meet quality and security standards.

The role will also shift toward more strategic thinking. With AI handling routine coding tasks, product managers and business technologists can focus on understanding user needs, designing better experiences, and making strategic decisions about feature priorities. The ability to translate business requirements into clear, AI-understandable context will be crucial.

We also see AI tools enabling smaller teams to build more sophisticated products, potentially changing how product teams are structured. Product managers might work more directly with AI-assisted developers, reducing the need for large development teams for certain types of projects.

However, this transformation also brings challenges. The need for human oversight, ethical considerations, and quality assurance will become even more critical. Business technologists and product managers will need to develop new skills in AI collaboration, prompt engineering, and verification processes while maintaining their core competencies in business analysis, user experience design, and strategic thinking.

---

## Conclusion

Our experience with AI-assisted development has been transformative. AI tools accelerated our development process, helped us explore design options, and caught potential issues early. However, we learned that AI is most effective when used as a collaborative partner with human oversight, not as an autonomous coder. The key to successful AI collaboration is maintaining clear context, thorough verification, and ethical transparency. As these tools continue to evolve, the roles of business technologists and product managers will shift toward more strategic, context-providing, and verification-focused responsibilities while maintaining their core value in understanding business needs and user experiences.

