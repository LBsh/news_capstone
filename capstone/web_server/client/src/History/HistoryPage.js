import './History.css';
import Auth from '../Auth/Auth';
import React from 'react';
import NewsCard from '../NewsCard/NewsCard';

class HistoryPage extends React.Component{

    constructor() {
        super();
        this.state = {news:null};
    }

    componentDidMount() {
        this.loadHistoryForUser();
    }

    loadHistoryForUser() {

        let url = 'http://localhost:3000/news/history/' + Auth.getEmail();
        
        let request = new Request(encodeURI(url), {
            method: 'GET',
            headers: {
                'Authorization': 'bearer ' + Auth.getToken()
            },
            cache: false
        });

        fetch(request)
            .then((res) => res.json())
            .then((historyNews) => {
                this.setState({
                    news: this.state.news ?
                        this.state.news.concat(historyNews) : historyNews
                });
            });

    }

    renderNews() {
        const news_list = this.state.news.map(function(news) {
            return (
                <a className='list-group-item' href='#'>
                    <NewsCard news={news} />
                </a>
            );
        });

        return (
            <div className='container-fluid'>
                <div className='list-group'>
                    {news_list}
                </div>
            </div>
        );
    }


    render() {
        if (this.state.news) {
            return (
                <div>
                    <br/>
                    {this.renderNews()}
                </div>

            );
        } else {
            return (
                <div>
                    {Auth.getUsername}. You currently have no browse history. Start reading news now!
                </div>
            )
        }
      
    }

}

export default HistoryPage;