import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from './config';
import { PlusIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

// Main application component for Writer Reports
// This will trigger the initial deployment to create gh-pages branch

interface Writer {
  id: string;
  name: string;
  articles: number;
  views: number;
  avg_views: number;
}

interface Summary {
  total_writers: number;
  total_articles: number;
  total_views: number;
  avg_views_per_article: number;
}

interface WriterData {
  writers: Writer[];
  summary: Summary;
}

function App() {
  const [data, setData] = useState<WriterData | null>(null);
  const [newWriterName, setNewWriterName] = useState('');
  const [isAddingWriter, setIsAddingWriter] = useState(false);
  const [startDate, setStartDate] = useState(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get<WriterData>(`${config.apiUrl}/writers`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const addWriter = async () => {
    try {
      await axios.post(`${config.apiUrl}/writers`, { name: newWriterName });
      setNewWriterName('');
      setIsAddingWriter(false);
      fetchData();
    } catch (error) {
      console.error('Error adding writer:', error);
    }
  };

  const updateStats = async (writerId: string, articles: number, views: number) => {
    try {
      await axios.put(`${config.apiUrl}/writers/${writerId}`, { articles, views });
      fetchData();
    } catch (error) {
      console.error('Error updating stats:', error);
    }
  };

  const deleteWriter = async (writerId: string) => {
    if (window.confirm('Are you sure you want to delete this writer?')) {
      try {
        await axios.delete(`${config.apiUrl}/writers/${writerId}`);
        fetchData();
      } catch (error) {
        console.error('Error deleting writer:', error);
      }
    }
  };

  if (!data) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;

  const { summary, writers } = data;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Writer Reports</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsAddingWriter(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              Add Writer
            </button>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-4 mb-8">
          {[
            { label: 'Total Writers', value: summary.total_writers },
            { label: 'Total Articles', value: summary.total_articles },
            { label: 'Total Views', value: summary.total_views.toLocaleString() },
            { label: 'Avg Views/Article', value: summary.avg_views_per_article },
          ].map((stat) => (
            <div key={stat.label} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">{stat.label}</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">{stat.value}</dd>
              </div>
            </div>
          ))}
        </div>

        {/* Writers Table */}
        <div className="bg-white shadow rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Articles</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Views</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {writers.map((writer, index) => (
                <tr key={writer.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">
                        {`${index + 1}.`} {writer.name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.articles}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.views.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.avg_views}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => {
                        const articles = prompt('Enter number of articles:', writer.articles.toString());
                        const views = prompt('Enter number of views:', writer.views.toString());
                        if (articles !== null && views !== null) {
                          updateStats(writer.id, parseInt(articles), parseInt(views));
                        }
                      }}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Update
                    </button>
                    <button
                      onClick={() => deleteWriter(writer.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Add Writer Modal */}
        {isAddingWriter && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
            <div className="bg-white rounded-lg p-6 max-w-sm w-full">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Writer</h3>
              <input
                type="text"
                value={newWriterName}
                onChange={(e) => setNewWriterName(e.target.value)}
                placeholder="Writer name"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <div className="mt-4 flex justify-end space-x-3">
                <button
                  onClick={() => setIsAddingWriter(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={addWriter}
                  disabled={!newWriterName.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
