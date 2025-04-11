import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""

#Custom CSS
st.markdown("""
<style>
    .main-header {
            font-size: 3rem !important;
            color: #1E3A8A;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
            text-shadow: 2px 2px 2px rgba(0,0,0,0.1);
        }
    .sub_header{
            font-size: 1.8rem !important;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

    .sucess-message {
            padding: 1rem;
            background-color: #ECFDF5;
            border-left: 5px solid #10B981;
            border-radius:  0.375rem;
}

    .warning-message {
            padding: 1rem;
            background-color: #FEF3C7;
            border-left: 5px solid #F59E0B;
            border-radius:  0.375rem;
            } 

    .book-card {
            background-color: #F3F4F6;
            border-radius: 0.5rem;
            padding: 1rem;
                margin-bottom: 1rem;
                border-left: 5px solid #3B82F6;
                transition: transform 0.3s ease;
            }
    .book-card-hover{
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1)
            }
    .read-badge {
            background-color: #10B981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
            }
    .unread-badge {
            background-color: #F87171;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .action-button {
            margin-right: 0.5rem;
            }
        .stButton>button {
            border-radius: 0.375rem;
        }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"Error loading Lottie animation: {e}")
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    if save_library():
        st.session_state.book_added = True
        time.sleep(0.5)  # Animation delay
        return True
    return False

def remove_book(index):
    try:
        del st.session_state.library[index]
        if save_library():
            st.session_state.book_removed = True
            return True
        return False
    except Exception as e:
        st.error(f"Error removing book: {e}")
        return False

def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        # Genre count
        genre = book["genre"]
        genres[genre] = genres.get(genre, 0) + 1

        # Author count
        author = book["author"]
        authors[author] = authors.get(author, 0) + 1

        # Decade count
        decade = (book["publication_year"] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

def create_visualizations(stats):
    if stats['total_books'] > 0:
        # Read status pie chart
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F7D2C4']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

        # Genres bar chart
        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values())
            })
            fig_genres = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color='Count',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig_genres.update_layout(
                title_text="Books by Genre",
                xaxis_title='Genre',
                yaxis_title='Number of Books',
                height=400
            )
            st.plotly_chart(fig_genres, use_container_width=True)

        # Decades line chart
        if stats['decades']:
            decades_df = pd.DataFrame({
                'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
                'Count': list(stats['decades'].values())
            })
            fig_decades = px.line(
                decades_df,
                x='Decade',
                y='Count',
                markers=True,
                line_shape="spline"
            )
            fig_decades.update_layout(
                title_text='Books by Publication Decade',
                xaxis_title='Decade',
                yaxis_title='Number of Books',
                height=400
            )
            st.plotly_chart(fig_decades, use_container_width=True)

# Load library data
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_1a8dx7zj.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')

nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

if nav_options == "View Library":
    st.session_state.current_view = 'library'
elif nav_options == 'Add Book':
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

# Main content area
st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input(
                "Publication Year",
                min_value=1000,
                max_value=datetime.datetime.now().year,
                value=2023
            )
        with col2:
            genre = st.selectbox(
                "Genre",
                ["Fiction", "Non-Fiction", "Biography", "Mystery", "Fantasy",
                 "Romance", "Poetry", "Self-Help", "Art", "Religion", "History", "Other"]
            )
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        
        if st.form_submit_button("Add Book"):
            if title and author:
                if add_book(title, author, publication_year, genre, read_bool):
                    st.success("Book added successfully!")
                    st.balloons()
                    st.session_state.book_added = False
                    st.rerun()
            else:
                st.warning("Please fill in all required fields (Title and Author)")

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", 
                    unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    new_status = not book['read_status']
                    btn_label = "✅ Mark as Read" if new_status else "📖 Mark as Unread"
                    if st.button(btn_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")
    
    if st.button("Search", key="search_btn"):
        if search_term.strip():
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_books(search_term, search_by.lower())
    
    if st.session_state.search_results:
        st.markdown(f"**Found {len(st.session_state.search_results)} results:**")
        for book in st.session_state.search_results:
            st.markdown(f"""
            <div class='book-card'>
                <h4>{book['title']}</h4>
                <p>Author: {book['author']}</p>
                <p>Year: {book['publication_year']} | Genre: {book['genre']}</p>
                <p>Status: <span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                    {"Read" if book["read_status"] else "Unread"}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.search_results == []:
        st.markdown("<div class='warning-message'>No books found matching your search criteria.</div>",
                    unsafe_allow_html=True)

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to see statistics!</div>",
                    unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Books Read", stats['read_books'])
        with col3:
            st.metric("Percentage Read", f"{stats['percent_read']:.1f}%")
        
        create_visualizations(stats)
        
        st.markdown("---")
        st.subheader("Additional Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Genres**")
            for genre, count in list(stats['genres'].items())[:5]:
                st.markdown(f"- {genre}: {count} books")
        
        with col2:
            st.markdown("**Top Authors**")
            for author, count in list(stats['authors'].items())[:5]:
                st.markdown(f"- {author}: {count} books")

st.markdown("---")
st.markdown("© 2024 Personal Library Manager | Developed with ❤️ by Streamlit", unsafe_allow_html=True)
