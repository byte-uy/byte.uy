---
layout: default
---

<div class="container">
    <section id="main_content">
        {% for post in site.posts %}
            <ul>
            <li><a href="{{ post.url }}">{{ post.date | date: "%-d %B %Y" }}</a></li>
            </ul>
            {% if post.layout == "post" %}
                <h1>{{ post.title }}</h1>
                <p>{{ post.excerpt }}</p>
                <a href="{{ post.url }}">Leer más</a>
            {% elsif post.layout == "image" %}
                <img src="{{ post.image }}" alt="{{ post.title }}" class="responsive rounded" />
                <p>{{ post.title }}</p>
            {% elsif post.layout == "micro" %}
                <p>{{ post.title }}</p>
            {% endif %}
        {% endfor %}
    </section>
</div>