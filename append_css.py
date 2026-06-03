import codecs
css = """
/* Contact Page Styles */
.contact-layout {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: 4rem;
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 0 6rem 0;
}

.contact-info {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.contact-info h3 {
    font-size: 1.5rem;
    color: var(--text-dark);
    margin-bottom: -1rem;
}

.contact-desc {
    color: var(--text-muted);
    line-height: 1.6;
}

.contact-method {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.cm-icon {
    width: 45px;
    height: 45px;
    border-radius: 12px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    font-size: 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.cm-details h4 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.25rem;
}

.cm-details p {
    color: var(--text-muted);
    font-size: 0.95rem;
}

.contact-socials {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.contact-socials a {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--bg-color);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-dark);
    transition: all 0.2s ease;
    text-decoration: none;
}

.contact-socials a:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
    transform: translateY(-2px);
}

.contact-form-container {
    background: white;
    padding: 2.5rem;
    border-radius: 24px;
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

.professional-form .form-row {
    display: flex;
    gap: 1.5rem;
}

.half-width {
    flex: 1;
}

.form-input {
    width: 100%;
    padding: 0.85rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--bg-color);
    font-family: inherit;
    font-size: 0.95rem;
    color: var(--text-dark);
    transition: border-color 0.2s, box-shadow 0.2s;
    box-sizing: border-box;
}

.form-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    background: white;
}

textarea.form-input {
    resize: vertical;
    min-height: 120px;
}

.w-100 {
    width: 100%;
    justify-content: center;
    padding: 1rem;
    font-size: 1rem;
}

@media (max-width: 768px) {
    .contact-layout {
        grid-template-columns: 1fr;
        gap: 3rem;
    }
    .professional-form .form-row {
        flex-direction: column;
        gap: 0;
    }
}
"""
with codecs.open('static/style.css', 'a', encoding='utf-8') as f:
    f.write(css)
