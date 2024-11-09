const sliderBox = document.querySelector('.slider-box')
const leftBtn = document.querySelector('.btn-left')
const rightBtn = document.querySelector('.btn-right')
const carouselImages = document.querySelectorAll('.slider-img')
const carouselWidth = 800

let index = 0


const handleCarousel = () => {
    index++
    changeImage()
}


const changeImage = () => {
    if(index > carouselImages.length - 1){
        index = 0
    } else if(index < 0 ){
        index = carouselImages.length - 1
    }

    sliderBox.style.transform = `translateX(${- index * carouselWidth}px)`
}

const handleRightArrow = () =>{
    index++
   
    resetInterval()
}
const handleLeftArrow = () =>{
    index--
    resetInterval()
}

const resetInterval = () => {
    changeImage()
    clearInterval(startCarousel)
}

rightBtn.addEventListener('click', handleRightArrow)
leftBtn.addEventListener('click', handleLeftArrow)
