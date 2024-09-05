import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../../Components/Sidebar/Sidebar";
import Navbar from "../../Components/Navbar/Navbar";
import "../../App.sass";
import { collection, query, getDocs, where } from "firebase/firestore";
import db from "../../firebase";
import html2PDF from "jspdf-html2canvas";

const InvoicePage = () => {
  const { id } = useParams();
  const [orders, setOrders] = useState({});
  const [customer, setCustomer] = useState({});
  const [tax, setTax] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);

  useEffect(() => {
    fetchOrderData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchOrderData = async () => {
    try {
      const orderDoc = await getDocs(query(collection(db, "orders"), where("id", "==", id)));
      const orderData = orderDoc.docs[0].data();
      setOrders(orderData);

      const customerDoc = await getDocs(query(collection(db, "customers"), where("id", "==", orderData.customer)));
      const customerData = customerDoc.docs[0].data();
      setCustomer(customerData);

      calculateTotal(orderData.orders);
    } catch (error) {
      console.error("Error fetching order data:", error);
    }
  };

  const calculateTotal = (orderItems) => {
    let total = 0;
    for (const productId in orderItems) {
      const product = orderItems[productId];
      const subtotal = product.quantity * product.price;
      total += subtotal;
    }
    setGrandTotal(total);
    // Assuming tax calculation logic here
    setTax(total * 0.1); // Example: 10% tax
  };



//const downloadPdf = async () => {
//  try {
//    const downloadButton = document.querySelector(".download-button");
//    downloadButton.style.display = "none";
//
//    await new Promise((resolve) => setTimeout(resolve, 100));
//
//    const page = document.querySelector(".invoice-page");
//
//    // Serialize the HTML content of the page
//    const htmlContent = new XMLSerializer().serializeToString(page);
//
//    // Send a POST request to the server to generate the PDF
//    const response = await fetch('/generate_pdf.php', {
//      method: 'POST',
//      headers: {
//        'Content-Type': 'application/json',
//      },
//      body: JSON.stringify({ htmlContent }),
//    });
//
//    if (!response.ok) {
//      throw new Error('Failed to generate PDF');
//    }
//
//    // Get the PDF blob from the response
//    const pdfBlob = await response.blob();
//
//    // Create a temporary URL for the PDF blob
//    const pdfUrl = URL.createObjectURL(pdfBlob);
//
//    // Create a link element to trigger the download
//    const link = document.createElement('a');
//    link.href = pdfUrl;
//    link.download = 'invoice.pdf';
//    document.body.appendChild(link);
//
//    // Trigger the click event to download the PDF
//    link.click();
//
//    // Clean up: remove the link and revoke the URL
//    document.body.removeChild(link);
//    URL.revokeObjectURL(pdfUrl);
//
//    downloadButton.style.display = "block";
//  } catch (error) {
//    console.error("Error generating PDF:", error);
//  }
//}

const downloadPdf = async () => {
  try {
    const downloadButton = document.querySelector(".download-button");
    downloadButton.style.display = "none";

    await new Promise((resolve) => setTimeout(resolve, 100));

    const page = document.querySelector(".invoice-page");

    // Serialize the HTML content of the page
    const htmlContent = new XMLSerializer().serializeToString(page);

    // Send HTML content to Flask server to generate PDF
    const response = await fetch('http://localhost:5000/generate_pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ htmlContent }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate PDF');
    }

    // Get the PDF blob from the response
    const pdfBlob = await response.blob();

    // Create a temporary URL for the PDF blob
    const pdfUrl = URL.createObjectURL(pdfBlob);

    // Create a link element to trigger the download
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = 'invoice.pdf';
    document.body.appendChild(link);

    // Trigger the click event to download the PDF
    link.click();

    // Clean up: remove the link and revoke the URL
    document.body.removeChild(link);
    URL.revokeObjectURL(pdfUrl);

    downloadButton.style.display = "block";
  } catch (error) {
    console.error("Error generating PDF:", error);
  }
}

  return (
    <main className="dashboard_container_main">
      <Sidebar />
      <div className="dashboard_container_right_panel">
        <Navbar />
        <div className="invoice-page container mt-4">
          <h3 className="text-center">Invoice letter</h3>
          <div className="row">
            <div className="col-md-12">
              <p>Invoice: {orders.invoice}</p>
              <p>Status: {orders.status}</p>
              <p>Customer name: {customer.name}</p>
              <p>Customer email: {customer.email}</p>
              <p>Contact no: {customer.contact}</p>

              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>Sr no</th>
                    <th>Name</th>
                    <th>Color</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Discount</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(orders.orders).map((key, index) => {
                    const product = orders.orders[key];
                    const discount = ((product.discount / 100) * product.price).toFixed(2);
                    const subtotal = (product.quantity * product.price - discount).toFixed(2);
                    return (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{product.name}</td>
                        <td>{product.color}</td>
                        <td>&#8377;{product.price}</td>
                        <td>{product.quantity}</td>
                        <td>{product.discount}% is {discount}</td>
                        <td>&#x20B9;{subtotal}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              <table className="table table-sm">
                <tr>
                  <td><a href="/" className="btn btn-sm btn-primary">Home </a></td>
                  <td><a href="#" className="btn btn-sm btn-success">Check out</a></td>
                  <td colSpan="3"><h4>Tax: &#x20B9;{tax}</h4></td>
                  <td colSpan="3"><h4>Grand total: &#x20B9;{grandTotal}</h4></td>
                  <td><button onClick={downloadPdf} className="btn btn-danger btn-sm float-right download-button">Generate pdf</button></td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};

export default InvoicePage;
