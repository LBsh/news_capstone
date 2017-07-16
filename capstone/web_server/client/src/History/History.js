import './History.css';
import Auth from '../Auth/Auth';
import React from 'react';
import NewsCard from '../NewsCard/NewsCard';

import _ from 'lodash';

class History extends React.Component{

    constructor() {
        super();
        this.state = {news:null};
        this.handleScroll = this.handleScroll.bind(this);
    }

    componentDidMount() {
        this.loadHistoryForUser();  
        this.loadHistoryForUser = _.debounce(this.loadMoreNews, 1000);      
        window.addEventListener('scroll', this.handleScroll);
    }

    handleScroll() {
        let scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
        if ((window.innerHeight + scrollY) >= (document.body.offsetHeight - 50)) {
            console.log('Loading more history...');
            this.loadMoreNews();
        }
    }


    loadHistoryForUser() {

        let url = 'http://localhost:3000/news/history';
        
        let request = new Request(url, {
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
                    Loading history...
                </div>
            )
        }
      
    }

}

export default History;