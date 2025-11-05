"""
Arquivo com livros de autores brasileiros, americanos, europeus e latinos
para popular a biblioteca
"""

LIVROS_EXEMPLO = [
    # ========== AUTORES BRASILEIROS ==========
    {
        "titulo": "Dom Casmurro",
        "autor": "Machado de Assis",
        "genero": "Romance",
        "preco": 35.90
    },
    {
        "titulo": "O Cortiço",
        "autor": "Aluísio Azevedo",
        "genero": "Romance",
        "preco": 32.50
    },
    {
        "titulo": "O Guarani",
        "autor": "José de Alencar",
        "genero": "Romance",
        "preco": 29.90
    },
    {
        "titulo": "Quarto de Despejo",
        "autor": "Carolina Maria de Jesus",
        "genero": "Diário",
        "preco": 28.00
    },
    {
        "titulo": "Grande Sertão: Veredas",
        "autor": "João Guimarães Rosa",
        "genero": "Romance",
        "preco": 45.00
    },
    {
        "titulo": "O Ateneu",
        "autor": "Raul Pompeia",
        "genero": "Romance",
        "preco": 27.80
    },
    {
        "titulo": "Capitães da Areia",
        "autor": "Jorge Amado",
        "genero": "Romance",
        "preco": 38.50
    },
    {
        "titulo": "A Hora da Estrela",
        "autor": "Clarice Lispector",
        "genero": "Romance",
        "preco": 33.00
    },
    {
        "titulo": "Vidas Secas",
        "autor": "Graciliano Ramos",
        "genero": "Romance",
        "preco": 31.20
    },
    {
        "titulo": "Mayombe",
        "autor": "Pepetela",
        "genero": "Romance",
        "preco": 36.00
    },

    # ========== AUTORES AMERICANOS ==========
    {
        "titulo": "1984",
        "autor": "George Orwell",
        "genero": "Distopia",
        "preco": 42.90
    },
    {
        "titulo": "O Apanhador no Campo de Centeio",
        "autor": "J.D. Salinger",
        "genero": "Romance",
        "preco": 37.50
    },
    {
        "titulo": "Matar um Rouxinol",
        "autor": "Harper Lee",
        "genero": "Romance",
        "preco": 39.90
    },
    {
        "titulo": "O Grande Gatsby",
        "autor": "F. Scott Fitzgerald",
        "genero": "Romance",
        "preco": 35.00
    },
    {
        "titulo": "Moby Dick",
        "autor": "Herman Melville",
        "genero": "Aventura",
        "preco": 48.00
    },
    {
        "titulo": "As Vinhas da Ira",
        "autor": "John Steinbeck",
        "genero": "Romance",
        "preco": 41.50
    },
    {
        "titulo": "O Sol é para Todos",
        "autor": "Harper Lee",
        "genero": "Romance",
        "preco": 38.00
    },
    {
        "titulo": "On The Road",
        "autor": "Jack Kerouac",
        "genero": "Romance",
        "preco": 36.80
    },
    {
        "titulo": "A Cor Púrpura",
        "autor": "Alice Walker",
        "genero": "Romance",
        "preco": 40.00
    },
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "genero": "Ficção Científica",
        "preco": 34.90
    },

    # ========== AUTORES EUROPEUS ==========
    {
        "titulo": "Dom Quixote",
        "autor": "Miguel de Cervantes",
        "genero": "Romance",
        "preco": 55.00
    },
    {
        "titulo": "Orgulho e Preconceito",
        "autor": "Jane Austen",
        "genero": "Romance",
        "preco": 32.90
    },
    {
        "titulo": "Crime e Castigo",
        "autor": "Fiódor Dostoiévski",
        "genero": "Romance",
        "preco": 46.80
    },
    {
        "titulo": "Guerra e Paz",
        "autor": "Liev Tolstói",
        "genero": "Romance",
        "preco": 68.00
    },
    {
        "titulo": "O Conde de Monte Cristo",
        "autor": "Alexandre Dumas",
        "genero": "Aventura",
        "preco": 52.50
    },
    {
        "titulo": "Madame Bovary",
        "autor": "Gustave Flaubert",
        "genero": "Romance",
        "preco": 36.00
    },
    {
        "titulo": "Ulisses",
        "autor": "James Joyce",
        "genero": "Romance",
        "preco": 58.90
    },
    {
        "titulo": "Cem Anos de Solidão",
        "autor": "Gabriel García Márquez",
        "genero": "Realismo Mágico",
        "preco": 44.50
    },
    {
        "titulo": "O Nome da Rosa",
        "autor": "Umberto Eco",
        "genero": "Romance",
        "preco": 47.00
    },
    {
        "titulo": "O Pequeno Príncipe",
        "autor": "Antoine de Saint-Exupéry",
        "genero": "Infantil",
        "preco": 25.00
    },

    # ========== AUTORES LATINOS ==========
    {
        "titulo": "Cem Anos de Solidão",
        "autor": "Gabriel García Márquez",
        "genero": "Realismo Mágico",
        "preco": 44.50
    },
    {
        "titulo": "O Jogo da Amarelinha",
        "autor": "Julio Cortázar",
        "genero": "Romance",
        "preco": 39.90
    },
    {
        "titulo": "A Casa dos Espíritos",
        "autor": "Isabel Allende",
        "genero": "Realismo Mágico",
        "preco": 41.00
    },
    {
        "titulo": "Ficções",
        "autor": "Jorge Luis Borges",
        "genero": "Contos",
        "preco": 36.80
    },
    {
        "titulo": "A Morte de Artemio Cruz",
        "autor": "Carlos Fuentes",
        "genero": "Romance",
        "preco": 35.50
    },
    {
        "titulo": "Pedro Páramo",
        "autor": "Juan Rulfo",
        "genero": "Romance",
        "preco": 30.00
    },
    {
        "titulo": "O Tambor",
        "autor": "Günter Grass",
        "genero": "Romance",
        "preco": 48.00
    },
    {
        "titulo": "A Festa do Bode",
        "autor": "Mario Vargas Llosa",
        "genero": "Romance",
        "preco": 46.50
    },
    {
        "titulo": "O Lobo da Estepe",
        "autor": "Hermann Hesse",
        "genero": "Romance",
        "preco": 38.90
    },
    {
        "titulo": "O Túnel",
        "autor": "Ernesto Sabato",
        "genero": "Romance",
        "preco": 32.00
    },

    # ========== AUTORES CONTEMPORÂNEOS ==========
    {
        "titulo": "Harry Potter e a Pedra Filosofal",
        "autor": "J.K. Rowling",
        "genero": "Fantasia",
        "preco": 39.90
    },
    {
        "titulo": "O Código Da Vinci",
        "autor": "Dan Brown",
        "genero": "Suspense",
        "preco": 42.00
    },
    {
        "titulo": "A Menina que Roubava Livros",
        "autor": "Markus Zusak",
        "genero": "Romance",
        "preco": 37.50
    },
    {
        "titulo": "O Hobbit",
        "autor": "J.R.R. Tolkien",
        "genero": "Fantasia",
        "preco": 45.00
    },
    {
        "titulo": "As Crônicas de Nárnia",
        "autor": "C.S. Lewis",
        "genero": "Fantasia",
        "preco": 52.00
    }
]

# Lista de autores por nacionalidade
AUTORES_BRASILEIROS = [
    "Machado de Assis", "Aluísio Azevedo", "José de Alencar", 
    "Carolina Maria de Jesus", "João Guimarães Rosa", "Raul Pompeia",
    "Jorge Amado", "Clarice Lispector", "Graciliano Ramos", "Pepetela"
]

AUTORES_AMERICANOS = [
    "George Orwell", "J.D. Salinger", "Harper Lee", "F. Scott Fitzgerald",
    "Herman Melville", "John Steinbeck", "Jack Kerouac", "Alice Walker",
    "Ray Bradbury", "Mark Twain"
]

AUTORES_EUROPEUS = [
    "Miguel de Cervantes", "Jane Austen", "Fiódor Dostoiévski", 
    "Liev Tolstói", "Alexandre Dumas", "Gustave Flaubert", 
    "James Joyce", "Umberto Eco", "Antoine de Saint-Exupéry",
    "Virginia Woolf"
]

AUTORES_LATINOS = [
    "Gabriel García Márquez", "Julio Cortázar", "Isabel Allende",
    "Jorge Luis Borges", "Carlos Fuentes", "Juan Rulfo",
    "Mario Vargas Llosa", "Ernesto Sabato", "Pablo Neruda"
]

def get_livros_por_autor(autor):
    """Retorna todos os livros de um autor específico"""
    return [livro for livro in LIVROS_EXEMPLO if livro["autor"] == autor]

def get_livros_por_genero(genero):
    """Retorna todos os livros de um gênero específico"""
    return [livro for livro in LIVROS_EXEMPLO if livro["genero"].lower() == genero.lower()]

def get_autores_por_nacionalidade(nacionalidade):
    """Retorna autores por nacionalidade"""
    if nacionalidade.lower() == "brasileiros":
        return AUTORES_BRASILEIROS
    elif nacionalidade.lower() == "americanos":
        return AUTORES_AMERICANOS
    elif nacionalidade.lower() == "europeus":
        return AUTORES_EUROPEUS
    elif nacionalidade.lower() == "latinos":
        return AUTORES_LATINOS
    else:
        return []