from html.parser import HTMLParser

class SimpleHTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.current_tag = None
        self.headers = []
        self.forms = []
        self.buttons = []
        self.div_ids = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        # Track div IDs
        if tag == 'div' and 'id' in attrs_dict:
            self.div_ids.append(attrs_dict['id'])
            
        # Track form IDs
        if tag == 'form' and 'id' in attrs_dict:
            self.forms.append(attrs_dict['id'])
            
        # Track buttons
        if tag == 'button':
            btn_str = f"id={attrs_dict.get('id')}" if 'id' in attrs_dict else "class=" + attrs_dict.get('class', '')
            self.buttons.append((btn_str, ""))
            
    def handle_data(self, data):
        data_clean = data.strip()
        if not data_clean:
            return
            
        # Track headers
        if self.current_tag in ['h1', 'h2', 'h3', 'h4']:
            self.headers.append(f"{self.current_tag}: {data_clean}")
            
        # Append button text if current tag is button
        if self.current_tag == 'button' and self.buttons:
            last_btn = self.buttons[-1]
            self.buttons[-1] = (last_btn[0], last_btn[1] + data_clean)
            
    def handle_endtag(self, tag):
        self.current_tag = None

def inspect(filename):
    print(f"=== {filename} ===")
    inspector = SimpleHTMLInspector()
    with open(f"static/{filename}", "r", encoding="utf-8") as f:
        inspector.feed(f.read())
        
    print("Top div IDs:", inspector.div_ids[:20])
    print("Forms found:", inspector.forms)
    print("Headers found:", inspector.headers[:15])
    print("Buttons found (first 10):", [f"{id_cls} ('{txt}')" for id_cls, txt in inspector.buttons[:10]])
    print("\n" + "="*40 + "\n")

inspect("dashboard.html")
inspect("analysis.html")
